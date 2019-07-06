FROM python:2.7-slim

LABEL name="FHIR FIELD" \
    description="FHIR Filed Plone" \
    maintainer="Plone Community"

ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8

# Install Python Setuptools
RUN apt-get update -y && \
    apt-get install -y locales git-core gcc g++ netcat libxml2-dev \
    libxslt-dev libz-dev python-dev libyaml-dev iputils-ping curl \
    libcurl4-openssl-dev apt-transport-https openssl libcurl4-openssl-dev ca-certificates

RUN mkdir /app

COPY requirements.txt /requirements.txt


# Install buildout
RUN pip install -r /requirements.txt
COPY . /app
RUN cd /app && buildout -c buildout.cfg
# RUN /app/bin/test
ENTRYPOINT ["/bin/bash", "-i", "-t"]
