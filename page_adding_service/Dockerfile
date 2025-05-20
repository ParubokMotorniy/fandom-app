FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y libpq-dev && pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

EXPOSE 8002

ENV CONSUL_HOST=192.168.56.2
ENV CONSUL_PORT=8500

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]