from fixtures import sdk
import time
from datetime import datetime, timedelta

def test_get_timestamp(sdk):
    with sdk as s:
        r = s.get_timestamp()
        assert isinstance(r['payload'], datetime)

def test_set_timestamp(sdk):
    now = datetime.today()
    with sdk as s:
        oldtime = s.get_timestamp()['payload']
        s.set_timestamp(now)
        r = s.get_timestamp()
        assert abs(r['payload'] - now) < timedelta(minutes=1)
        s.set_timestamp(oldtime)
