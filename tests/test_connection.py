from fixtures import sdk
from argos import exceptions
import pytest


def test_connection(sdk):
    with sdk as s:
        print("ok!")
    print("ok, disconnected")


def test_command_timeout(sdk):
    with sdk as s:
        with pytest.raises(exceptions.SendCommandTimeout) as excinfo:
            cards = s.get_cards(5, 0, timeout=0.01, tries=0)
