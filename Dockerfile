FROM python:3.8 AS declaraciones_py
RUN mkdir /code
RUN apt-get update -y && apt-get  -y install build-essential gcc uwsgi && apt-get clean
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils

# Add docker-compose-wait tool -------------------
ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

WORKDIR /code
