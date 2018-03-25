[![Build Status](https://travis-ci.org/drmobile/pubsub-lib.svg?branch=master)](https://travis-ci.org/drmobile/pubsub-lib)

# pubsub-broker

A generic purpose google cloud pub/sub broker to dispatch subscribed topics.

## Prerequisites

* Python 3.5+ is required for ayncio.
* [Setting Up Authentication for Server to Server Production Applications](https://cloud.google.com/docs/authentication/production)
    1. Go to the **Create service account key** page in the GCP Console.
    2. From the **Service account** drop-down list, select **New service account**.
    3. Input a name into the **Service account name** field.
    4. From the **Role** drop-down list, select **Project > Owner**.
    5. Click **Create**. A JSON file that contains your key downloads to your computer.

* Environment Variables

```
export PUBSUB_EMULATOR_HOST=localhost:8432
export PUBSUB_PROJECT_ID=my-project-id
```

* Development in emulator

    1. Starting pubsub emulator
        ```docker run --rm --tty --interactive -p 8538:8538 bigtruedata/gcloud-pubsub-emulator start --host-port=0.0.0.0:8538 --data-dir=/data```
    2. Setting the variables
        ```export PUBSUB_EMULATOR_HOST=127.0.0.1:8538```
