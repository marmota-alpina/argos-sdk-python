from fixtures import sdk
from datetime import datetime, timedelta


def test_get_events(sdk):
    d = datetime.today() - timedelta(days=1)
    with sdk as s:
        events = s.get_events(start_date=d)["payload"]
        assert isinstance(events, list)
