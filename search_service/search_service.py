from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse

from  . import search_results_helper as helper

from pathlib import Path

from elasticsearch import AsyncElasticsearch
from confluent_kafka import Consumer, KafkaException

from ..consul import consul_helpers as ch

import os
import threading
import numpy as np

search_service = FastAPI()

def poll_pages():
    while True:
        try:
            incoming_message = search_service.state.kafka_consumer.poll()

            if incoming_message is None:
                continue
            if incoming_message.error():
                raise KafkaException(incoming_message.error())
            else:
                # TODO: properly receive the page from the queue
                # TODO: obtain the URI from the queue
                # TODO: obtain page id from the queue

                # messenger_service.state.local_message_map[incoming_message.key().decode('utf-8')] = incoming_message.value().decode('utf-8')
                # print(f"Messenger {os.getpid()} received message: {incoming_message.key().decode('utf-8')}:{incoming_message.value().decode('utf-8')}")

                search_service.state.kafka_consumer.commit(incoming_message)
        except Exception as e:
            # probably consumer was closed
            print(f"Polling {os.getpid()} stopped!")
            break

@search_service.get("/search/get_matches", response_class=HTMLResponse)
async def search_pages(query_string: str):
    try:
        response = await search_service.state.elastic_client.search(
            index=search_service.state.page_index_name,
            size=15,
            query={
                "multi_match": {"query": query_string, "fields": ["title^2", "content"]}
            },
            _source=["title", "uri"],
        )
    except Exception as e:
        print(f"Failed to query db for matching pages. Details: {e}")

    print(f"Raw search result: {response}")

    if response["hits"]["total"]["value"] == 0:
        return helper.construct_empty_search_page()

    results = [
        (hit["_source"]["title"], hit["_source"]["uri"])
        for hit in response["hits"]["hits"]
    ]
    
    if len(results) == 0:
        return helper.construct_empty_search_page()

    uris = [url for _, url in results]
    thumbs = [title for title, _ in results]
    return helper.construct_search_results_page(uris, thumbs)

#to be used in debugging purposes only
@search_service.post("/search/post_page")
async def add_page_debug(new_page: UploadFile):
    if new_page.content_type == "text/html":
        contents = await new_page.read()

        new_doc = helper.construct_elastic_entry(contents, "https://aa.bb.cc/")

        try:
            await search_service.state.elastic_client.create(
                index=search_service.state.page_index_name, document=new_doc, id=np.random.randint(0,1000000)
            )
        except Exception as e:
            print(f"Failed to index a page. Details: {e}")
            raise HTTPException(status_code=503, detail="Some elasticsearch error!")


@search_service.on_event("shutdown")
async def terminate_search():
    search_service.state.kafka_consumer.close()
    search_service.state.elastic_client.close()
    search_service.state.polling_thread.join()
    
    print(f"Search service {os.getpid()} terminated gracefully!")
    
@search_service.get("/health")
async def check():
    return "Search is healthy"

@search_service.on_event("startup")
async def start_search():
    #elastic
    elastic_service = ch.get_random_service("elasticsearch")
    
    print(f"Obtained elastic config: {elastic_service}")
    
    if elastic_service == None:
        print("Search service failed to connect to elastic!")
        return
        
    search_service.state.elastic_client = AsyncElasticsearch(
        f"https://{elastic_service[0]}:{elastic_service[1]}",
        http_auth=(os.environ["ELASTIC_USER"], os.environ["ELASTIC_PASSWORD"]),
        ca_certs=str(Path(__file__).parent/"./http_ca.crt"), #certificates had better be stored locally
        verify_certs=True
    )
    
    #kafka
    general_kafka_config = ch.read_value_for_key("kafka-config")
    
    print(f"Obtained kafka config: {general_kafka_config}")
    
    custom_kafka_config = {
    **general_kafka_config["kafka_parameters"],    
    "auto.offset.reset": "earliest",
    "enable.auto.commit": True
    }
        
    search_service.state.kafka_consumer = Consumer(custom_kafka_config)
    search_service.state.kafka_consumer.subscribe([general_kafka_config["search-topic-name"]])
    
    #sevice-specific stuff
    ch.register_consul_service("search", "0", os.environ["INSTANCE_HOST"], int(os.environ["INSTANCE_PORT"]), 30, 60, "/health" )

    search_service.state.polling_thread = threading.Thread(
        target=poll_pages, name="Poller", daemon=True
    )
    search_service.state.polling_thread.start()

    search_service.state.page_index_name = "fandom_pages"

    print(f"Search service {os.getpid()} started gracefully!")
