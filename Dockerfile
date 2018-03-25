FROM python:alpine3.4

RUN mkdir -p /var/pubsub/broker
RUN mkdir -p /var/log/broker
WORKDIR /var/pubsub/broker

# Provide GCP credentials by setting environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS=/var/pubsub/broker/pubsub-trial-f5e6dbba824c.json

# (Alpine) Install required packages and remove the apk packages cache when done.
RUN apk update
RUN apk add --update build-base linux-headers
RUN rm -rf /var/cache/apk/*

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD app.py /var/pubsub/broker
ADD pubsub-trial-f5e6dbba824c.json /var/pubsub/broker
COPY ./soocii_pubsub_lib /var/pubsub/broker/soocii_pubsub_lib

# Setup container version in order to workaround error
# One or more build-args [VERSION] were not consumed, failing build.
ARG version
ENV CONTAINER_VERSION ${version}

ENTRYPOINT ["/var/pubsub/broker/app.py"]
