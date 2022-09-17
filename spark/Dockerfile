FROM python:3.8

MAINTAINER Cristofero Catania

EXPOSE 4040

WORKDIR /contents

ADD requirements.txt .
ADD https://downloads.apache.org/spark/spark-3.1.3/spark-3.1.3-bin-hadoop3.2.tgz .

RUN apt update -y && apt install -y tar netcat openjdk-11-jdk

ENV JAVA_HOME=/usr

RUN python3 -m pip install --upgrade pip setuptools
RUN python3 -m pip install -r requirements.txt
#RUN pip install pandas flickrapi requests pyspark elasticsearch

RUN tar -xzf spark-3.1.3-bin-hadoop3.2.tgz

WORKDIR /contents/spark-3.1.3-bin-hadoop3.2

ADD main.py .

CMD [ "bin/spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1,org.elasticsearch:elasticsearch-spark-30_2.12:7.12.1", "main.py" ]