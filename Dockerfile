FROM python:alpine

MAINTAINER Vinicius Schettino <vinicius.schettino@ufjf.edu.br>


RUN mkdir -p /sdk
WORKDIR /sdk
COPY . .

RUN python -m pip install --upgrade pip
RUN python -m pip install --upgrade -r ./requirements.txt

CMD sh ./test_script 
