FROM alpine:3.14.0

MAINTAINER Cristofero Catania

EXPOSE 9092

WORKDIR /contents

ADD https://downloads.apache.org/kafka/2.8.2/kafka_2.13-2.8.2.tgz .

RUN apk add --no-cache bash tar sed openjdk11

ENV JAVA_HOME=/usr

ARG ZOOKEEPER_HOST
ARG KAFKASERVER_HOST

RUN tar -xzf kafka_2.13-2.8.2.tgz

WORKDIR /contents/kafka_2.13-2.8.2

RUN sed -i "0,/zookeeper.connect=localhost:2181/s//zookeeper.connect=${ZOOKEEPER_HOST}/" config/server.properties
RUN sed -i "0,/#listeners=PLAINTEXT:\/\/:9092/s//listeners=PLAINTEXT:\/\/:9092/" config/server.properties
RUN sed -i "0,/#advertised.listeners=PLAINTEXT:\/\/your.host.name:9092/s//advertised.listeners=PLAINTEXT:\/\/${KAFKASERVER_HOST}/" config/server.properties

CMD [ "/bin/bash", "bin/kafka-server-start.sh", "config/server.properties" ]