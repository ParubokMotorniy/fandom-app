FROM python:3.11-slim

WORKDIR /app

COPY __init__.py ./auth_service.py ./requirements.txt ./
COPY ./consul_helpers.py ./consul_h/
RUN pip install --no-cache-dir -r requirements.txt

RUN ls
RUN ls ./consul_h
EXPOSE 9100

ENTRYPOINT ["uvicorn", "auth_service:auth_service", "--host", "0.0.0.0", "--port", "9100"]
