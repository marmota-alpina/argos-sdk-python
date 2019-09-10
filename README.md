# SDK for Henry Argos Biometric Fingerprint

Henry Argos SDK is a helper project to handle communication with [Henry Argos](http://www.henry.com.br/controle-de-acesso/argos) access control fingerprint/card reader. All communication happens through TCP/IP sockets, where the reader is the server and this SDK plays the client role.

## Compability
The protocol should be compatible with other [Henry products](https://www.henry.com.br/controle-de-acesso), but many features were tailored down to Argos use, since this is the main goal of the project. Given it time, the goal is to remain compatible and feature balanced with other products as well. All development, use and automated testing were conducted using Argos firmware versions **1.0.1.3b** and **1.0.0.24**.

## Basic install

You can install it from pip like:
```bash
pip install ArgosSDK
```
It has the following dependencies:
1. Python 3.6+
1. [Daiquiri](https://daiquiri.readthedocs.io/) for logging
1. [Parse](https://pypi.org/project/parse/) for handling package parsing.

## Basic usage
In the basic usage you only need to import the SDK and the exceptions for error handling:

```python
from argos import SDK, exceptions
from datetime import datetime, timedelta
import daiquiri, logging

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger()

ip = "192.168.0.200"
fingerprints = [
    "putsomefingerprintshere",
    "putanotherfingerprinthere"
]
now = datetime.today()
d = now - timedelta(days=1)
try:
    with SDK(ip) as s:
        s.set_timestamp(timestamp=now).data
        s.get_timestamp()
        s.get_cards(count=14, start_index=0)
        s.get_quantity(type=SDK.QT_CARDS)
        s.send_cards(card_number="TEST")
        s.capture_fingerprint(card_number="47854785", timeout=30)
        s.get_fingerprints(card_number="47854785")
        s.send_fingerprints("47854785", fingerprints)
        s.delete_fingerprints(card_number="47854785")
        s.send_cards(card_number="47854785", mode=SDK.SEND_DELETE)
        s.get_events(start_date=d)
except (
    exceptions.ConnectTimeout,
    exceptions.SendCommandTimeout,
    exceptions.ResponseParsing,
    exceptions.TooManyCardsRequested,
    exceptions.GenericErrorResponse,
) as e:
    logger.warning(e)
```

Besides the IP, you can also specify the following parameters to the SDK:

1. `port` (default 3000)
1. `timeout`, meaning the default time the socket should hang while expecting a response. Valid to the connection procedure. (default 3s)
1. `max_tries` specifies how many times the command should be resend before it gives up. (default 5 times)
1. `sleep_between_tries` meaning how much the SDK should wait before sending again the command. (default .5s)


## Commands

# Command send configuration
Every command can receive the following ``**connection_params``:

1. `timeout` overrides the SDK configuration on how much the socket should hang while expecting a response.
1. `tries` overrides the SDK configuration on how many times the command should be resend before it gives up.

## Command list

### SDK.get_timestamp([\*\*conection_params])
Get the current timestamp setted on the equipment.

**Expects**: None

**Returns**: datetime object

## Basic package protocol information

## Create your own command

## #ToDo stuff
1. Use checksum byte in order to verify

## Building and testing

## About this Project
