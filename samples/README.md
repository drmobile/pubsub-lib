# Sample Application

## Prerequisites

* [Setting Up Authentication for Server to Server Production Applications](https://cloud.google.com/docs/authentication/production)
    1. Go to the **Create service account key** page in the GCP Console.
    2. From the **Service account** drop-down list, select **New service account**.
    3. Input a name into the **Service account name** field.
    4. From the **Role** drop-down list, select **Project > Owner**.
    5. Click **Create**. A JSON file that contains your key downloads to your computer.

## Build Docker Image

1. download pub/sub credential and copy to this folder (./samples/pubsub-trial.json)

2. build docker

```
docker build -t broker .
```

3. start subscriber service

```
docker run broker
```
