
FROM python:3.10.5-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .

WORKDIR /app/


RUN apt-get update
RUN apt-get install -y curl

ARG ENVIRONMENT=dev

COPY . /app/

RUN pip install -r requirements.txt

COPY ./startup.sh /app/

RUN chmod +x /app/startup.sh
