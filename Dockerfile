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

RUN pip install soocii-pubsub-lib==0.8

ADD app.py /var/pubsub/broker
ADD pubsub-trial-f5e6dbba824c.json /var/pubsub/broker

ENTRYPOINT ["/var/pubsub/broker/app.py"]
