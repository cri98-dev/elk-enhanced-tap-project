FROM alpine:3.14.0

MAINTAINER Cristofero Catania

EXPOSE 2181

WORKDIR /contents

ADD https://downloads.apache.org/kafka/2.8.1/kafka_2.13-2.8.1.tgz .

RUN apk add --no-cache bash tar openjdk11

ENV JAVA_HOME=/usr

RUN tar -xzf kafka_2.13-2.8.1.tgz

WORKDIR /contents/kafka_2.13-2.8.1

CMD [ "/bin/bash", "bin/zookeeper-server-start.sh", "config/zookeeper.properties" ]