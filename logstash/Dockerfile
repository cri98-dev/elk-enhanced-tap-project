FROM ubuntu

MAINTAINER Cristofero Catania

WORKDIR /contents

ADD https://artifacts.elastic.co/downloads/logstash/logstash-8.2.2-linux-x86_64.tar.gz .

RUN tar -xzf logstash-8.2.2-linux-x86_64.tar.gz

WORKDIR /contents/logstash-8.2.2

COPY logstash.conf ./config

CMD ["bin/logstash", "-f", "config/logstash.conf"]