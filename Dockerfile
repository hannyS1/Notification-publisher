FROM python:3.8

RUN apt-get update

WORKDIR /server

COPY ./ /server
RUN pip install -r /server/requirements.txt

