# coding=utf-8
#
import os
import docker
import pytest

container = None


@pytest.fixture()
def no_emulator(request):
    # export PUBSUB_EMULATOR_HOST=127.0.0.1:8538
    os.environ["PUBSUB_EMULATOR_HOST"] = "127.0.0.1:8538"


@pytest.fixture()
def start_emulator(request):
    # export PUBSUB_EMULATOR_HOST=127.0.0.1:8538
    os.environ["PUBSUB_EMULATOR_HOST"] = "127.0.0.1:8538"

    # start pubsub emulator
    client = docker.from_env()
    container = client.containers.run(
        'bigtruedata/gcloud-pubsub-emulator',
        'start --host-port=0.0.0.0:8538 --data-dir=/data',
        ports={'8538/tcp': 8538},
        detach=True,
        auto_remove=True)

    def stop_emulator():
        container.stop()

    request.addfinalizer(stop_emulator)
    return container
