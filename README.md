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
        s.set_timestamp(timestamp=now)
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

# Command response
Commands always return a `Response` object. If you want to access the returned data, you can simply use it as a dict:

```python
with SDK(ip) as s:
    response = s.set_timestamp(timestamp=now)
    print(response) # print the response dict repr()
    print(response.data) # the actual dict with the response data
    print(response['payload']) # the payload of the response, already parsed

```

If the return code is **greater than 10**, it means something went wrong. A `GenericErrorResponse` or one of its children will be raised containing more information.

## Command list

### SDK.get_timestamp([\*\*conection_params])
Get the current timestamp setted on the equipment.

**Expects**: None

**Returns**: datetime object

### SDK.set_timestamp([timestamp], [\*\*conection_params])
Set the current timestamp setted on the equipment.

**Expects**: Datime object. If none, `datetime.now()` will be used instead.

**Returns**: No payload.

### SDK.get_cards(count, start_index, [\*\*conection_params])
Retrieve the cards registered, between `[start_index, start_index+count]`.
The protocol here limitates the response into 30 cards. If you try to get more than
that, a `TooManyCardsRequested` will be raised.

**Expects**:
1. `count`: how many cards
1. `start_index`: from index. These parameters work like SQL's [LIMIT and OFFSET](http://www.sqltutorial.org/sql-limit/)

**Returns**: payload containing `count` cards on a list

### SDK.get_quantity([type, \*\*conection_params])
Get the count of a given entry type.


**Expects**: Type. The options are:

1. SDK.QT_USERS = "U"
1. SDK.QT_CARDS = "C"
1. SDK.QT_FINGERPRINTS = "D"
1. SDK.QT_MAX_FINGERPRINTS = "TD"

**Returns**: a String containing a numeric value.

### SDK.send_cards([card_number, [master], [verify_fingerprint], [send_mode]\*\*conection_params])
Get the current timestamp setted on the equipment.

**Expects**:
1. `card_number` MAX 20
1. `master` the card type, being:
  - SDK.NORMAL_MODE ('1') without master access (default)
  - SDK.MASTER_MODE ('6') master access
1. `verify_fingerprint` whether the fingerprint is required to validate access (default True)
1. `send_mode` the way the command should be send, being:
  - SEND_INSERT = "I" (default)
  - SEND_UPDATE = "A"
  - SEND_DELETE = "E"  (complete wipe out, be careful)

**Returns**: No payload

### SDK.send_fingerprints(card_number, fingerprints[\*\*conection_params])
Send a list of fingerprints to the reader.

**Expects**:
1. `card_number` MAX 20 (must be registered already)
1. `fingerprints` a list of fingerprints as hex strings.

**Returns**: No payload


## Basic package protocol information

## Create your own command

## #ToDo stuff
1. Use checksum byte in order to verify package integrity. Today it only verifies the start/end bytes.
1. Send more than one card at time.

## Building and testing

## About this Project
