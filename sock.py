from argos import ArgosSocket, responses, exceptions
from argos.commands import SetTimestamp, GetTimestamp
import daiquiri, logging

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger()

ips = [
    "10.15.21.215",
    "10.15.21.203",
    "10.15.21.214",
    "10.15.21.219",
    "10.15.21.200",
    "10.15.21.211",
    "10.15.21.213",
    "10.15.21.220",
    "10.15.21.208",
    "10.15.21.212",
    "10.15.21.204",
    "10.15.21.205",
    "10.15.21.206",
    "10.15.21.216",
    "10.15.21.217",
    "10.15.21.218",
]
for ip in ips:
    try:
        with ArgosSocket(ip) as s:
            response = s.send_command(SetTimestamp())
            if response.status():
                get_response = s.send_command(GetTimestamp())
                print(get_response["timestamp"])
    except (
        exceptions.ConnectTimeout,
        exceptions.SendCommandTimeout,
        exceptions.ResponseParsing,
    ) as e:
        logger.warning(e)
