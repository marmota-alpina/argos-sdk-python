from argos import ArgosSocket, responses, exceptions
from argos.commands import GetTimestamp
import daiquiri, logging

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger()

ips = [
    "10.15.21.215",
    "10.15.21.203",
    "10.15.21.214",
    "10.15.21.219",
    "10.15.21.201",
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
            output = s.send_command(GetTimestamp())
            response = responses.GetTimestamp(output)
            print(response["timestamp"])
    except exceptions.ConnectTimeout as e:
        logger.warning(e)
