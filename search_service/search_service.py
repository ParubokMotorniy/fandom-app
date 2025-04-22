from fastapi import FastAPI, HTTPException
from fastapi.
from fastapi.responses import HTMLResponse
import search_results_helper as helper
from elasticsearch import Elasticsearch, AsyncElasticsearch
from confluent_kafka import Consumer, KafkaException
import os
import threading

#GET -> receive a search string (that simple for now) -> query db -> build a list of matches -> return the list

kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id':          'kafka-servitor',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit' : True
}

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
                #TODO: properly receive the page from the queue
                #TODO: obtain the URI somehow 
                
                # messenger_service.state.local_message_map[incoming_message.key().decode('utf-8')] = incoming_message.value().decode('utf-8') 
                # print(f"Messenger {os.getpid()} received message: {incoming_message.key().decode('utf-8')}:{incoming_message.value().decode('utf-8')}")
                
                search_service.state.kafka_consumer.commit(incoming_message)
        except RuntimeError as e:
            #probably consumer was closed
            print(f"Polling {os.getpid()} stopped!")

@search_service.get("/search/get_matches", response_model=HTMLResponse)
async def search_pages(query_string: str):
    response = await search_service.state.elastic_client.search(
        index=search_service.state.page_index_name,
        size=15,
        query={
            "multi_match": {
                "query": query_string,
                "fields": ["title^2", "content"]
            }
        },
        _source=["title", "uri"]
    )
    
    print(f"Raw search result: {response}")

    results = [(hit["_source"]["title"], hit["_source"]["url"]) for hit in response["hits"]["hits"]]
    
    uris = [url for _, url in results]
    thumbs = [title for title, _ in results]
    return helper.construct_search_results_page(uris, thumbs)

#TODO: force html input here
@search_service.post("/search/post_page")
async def add_page(new_page: str):
    #TODO: obtain URI somehow
    new_doc = helper.construct_elastic_entry(new_page, "https://aa.bb/")
    
    await search_service.state.elastic_client.index(index=search_service.state.page_index_name, document=new_doc) 
    
@search_service.on_event("shutdown")
async def terminate_search():
    search_service.state.kafka_consumer.close()
    search_service.state.elastic_client.close()
    print(f"Search service {os.getpid()} terminated gracefully!")
    
@search_service.on_event("startup")
async def start_search():
    search_service.state.kafka_consumer = Consumer(kafka_config)
    
    search_service.state.elastic_client = AsyncElasticsearch("hhtp://localhost:9200", client_cert="./http_ca.crt", client_key=os.environ['ES_PASS'])
    
    search_service.state.polling_thread = threading.Thread(target=poll_pages,name="Poller",daemon=True)
    search_service.state.polling_thread.start()
    
    search_service.state.page_index_name = "fandom_pages"
    
    print(f"Search service {os.getpid()} started gracefully!")

    