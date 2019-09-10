from fixtures import sdk
from argos import exceptions
import time
import pytest


def test_add_new_card_ok(sdk):
    with sdk as s:
        s.send_cards("12345671")


def test_remove_card_ok(sdk):
    with sdk as s:
        s.send_cards("67289572")
        s.send_cards("67289572", mode=sdk.SEND_DELETE)


def test_remove_card_notfound(sdk):
    with sdk as s:
        # the protocol really does not complain, so...
        s.send_cards("12345672", mode=sdk.SEND_DELETE)


def test_get_cards(sdk):
    with sdk as s:
        cards = s.get_cards(16, 0)["payload"]
        assert isinstance(cards, list)


def test_get_too_many_cards(sdk):
    with sdk as s:
        with pytest.raises(exceptions.TooManyCardsRequested) as excinfo:
            cards = s.get_cards(300, 0)
