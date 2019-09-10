from fixtures import sdk


def test_get_quantity_cards(sdk):
    with sdk as s:
        r = s.get_quantity(type=sdk.QT_CARDS)
        assert int(r["payload"])


def test_get_quantity_users(sdk):
    with sdk as s:
        r = s.get_quantity(type=sdk.QT_USERS)
        assert int(r["payload"]) >= 0


def test_get_quantity_fingerprints(sdk):
    with sdk as s:
        r = s.get_quantity(type=sdk.QT_FINGERPRINTS)
        assert int(r["payload"]) >= 0
