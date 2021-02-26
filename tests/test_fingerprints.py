from fixtures import sdk, fingerprints
from argos import exceptions
import pytest
import time


def test_send_fingerprint(sdk, fingerprints):
    with sdk as s:
        s.send_cards("12332145")
        s.send_fingerprints("12332145", fingerprints, timeout=10)
        s.send_cards("12332145", mode=sdk.SEND_DELETE)


def test_delete_fingerprints(sdk, fingerprints):
    with sdk as s:
        s.send_cards("24142112")
        s.send_fingerprints("24142112", fingerprints, timeout=10)
        s.delete_fingerprints("24142112")


def test_get_fingerprints(sdk, fingerprints):
    with sdk as s:
        s.send_fingerprints("12487984", fingerprints, timeout=10)
        new_fingerpints = s.get_fingerprints("12487984", timeout=10)["payload"]
        assert [f in fingerprints for f in new_fingerpints]


def test_delete_fingerprints_empty_card(sdk):
    with sdk as s:
        s.send_cards("66167878")
        with pytest.raises(exceptions.GenericErrorResponse) as excinfo:
            s.delete_fingerprints("66167878")
