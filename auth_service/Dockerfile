FROM python:3.11-slim

WORKDIR /app

COPY __init__.py ./auth_service.py ./requirements.txt ./
COPY __init__.py ./consul_helpers.py ./consul/
RUN pip install --no-cache-dir -r requirements.txt

RUN ls
RUN ls ./consul
EXPOSE 9400

ENTRYPOINT ["uvicorn", "auth_service:auth_app", "--host", "0.0.0.0", "--port", "9100"]
