FROM python:3

RUN apt-get -y update \
    && pip install argparse 

WORKDIR /usr/src/app

COPY inquisitor.py .

RUN ["tail", "-f", "/dev/null"]