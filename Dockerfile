FROM python:alpine3.4

RUN mkdir -p /var/pubsub/broker
RUN mkdir -p /var/log/broker
WORKDIR /var/pubsub/broker

# (Alpine) Install required packages and remove the apk packages cache when done.
RUN apk update
RUN apk add --update build-base linux-headers
RUN rm -rf /var/cache/apk/*

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY ./app /var/pubsub/broker

# Setup container version in order to workaround error
# One or more build-args [VERSION] were not consumed, failing build.
ARG version
ENV CONTAINER_VERSION ${version}

