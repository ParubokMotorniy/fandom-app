FROM python:3.11-slim 

WORKDIR /search_service/

COPY ./search_results_helper.py ./search_service.py ./requirements.txt ./http_ca.crt /search_service/

RUN pip install -r ./requirements.txt

EXPOSE 9300 9096 9200

ENTRYPOINT ["fastapi", "run", "./search_service.py", "--port", "9300"]

