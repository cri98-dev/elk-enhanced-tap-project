FROM python:3.8

MAINTAINER Cristofero Catania

EXPOSE 8080

WORKDIR /contents

ADD torchvisionModel_standalone.py .
ADD https://download.pytorch.org/models/convnext_large-ea097f82.pth .
ADD requirements.txt .

RUN python3 -m pip install --upgrade pip setuptools
RUN python3 -m pip install -r requirements.txt

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "torchvisionModel_standalone:app" ]