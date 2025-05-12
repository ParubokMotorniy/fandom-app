FROM python:3.11-slim 

WORKDIR /search_service/

COPY ./__init__.py ./search_results_helper.py ./search_service.py ./requirements.txt ./http_ca.crt /search_service/search/
COPY ./__init__.py ./consul_helpers.py  /search_service/consul/
COPY ./__init__.py /search_service/

WORKDIR /search_service/search

RUN pip install -r ./requirements.txt

EXPOSE 9300

ENTRYPOINT ["fastapi", "run", "--port", "9300", "./search_service.py"]

