FROM python:3-slim

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./exporter.py .

USER 1000

STOPSIGNAL SIGINT

ENTRYPOINT ["python", "./exporter.py"]
