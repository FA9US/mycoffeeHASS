"""Blocking cloud operations. Run only in Home Assistant's executor."""

from .aromatic_cloud.account import CheckError, login_devices, owned_machine
from .aromatic_cloud.wake import ACKNOWLEDGED, wake_once


def authenticate(data):
    token, devices = login_devices(data["email"], data["password"], data["app_client_id"])
    return owned_machine(devices, data["serial"].strip()), token


def warm_up(data):
    machine, token = authenticate(data)
    result = wake_once(machine, token)
    if result != ACKNOWLEDGED:
        raise CheckError(result)
