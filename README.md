[![Build Status](https://travis-ci.org/drmobile/pubsub-lib.svg?branch=master)](https://travis-ci.org/drmobile/pubsub-lib)
[![Coverage Status](https://coveralls.io/repos/github/drmobile/pubsub-lib/badge.svg?branch=master)](https://coveralls.io/github/drmobile/pubsub-lib?branch=master)

# pubsub-lib

A generic purpose google cloud pub/sub broker to dispatch subscribed topics.

## Prerequisites

* Python 3.5+ is required for ayncio.
* [Setting Up Authentication for Server to Server Production Applications](https://cloud.google.com/docs/authentication/production)
    1. Go to the **Create service account key** page in the GCP Console.
    2. From the **Service account** drop-down list, select **New service account**.
    3. Input a name into the **Service account name** field.
    4. From the **Role** drop-down list, select **Project > Owner**.
    5. Click **Create**. A JSON file that contains your key downloads to your computer.
