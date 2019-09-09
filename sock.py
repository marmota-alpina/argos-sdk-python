from argos import ArgosSocket, responses, exceptions
from datetime import datetime, timedelta
from argos.commands import (
    SetTimestamp,
    GetTimestamp,
    GetCards,
    GetQuantity,
    SendCards,
    GetFingerprints,
    DeleteFingerprints,
    CaptureFingerprint,
    SendFingerprints,
    GetEvents,
)
import daiquiri, logging

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger()

ips = [
    #    "10.15.21.202",
    "10.15.21.221",
    #    "10.15.21.203",
    #    "10.15.21.214",
    #    "10.15.21.219",
    #    "10.15.21.200",
    #    "10.15.21.211",
    #    "10.15.21.213",
    #    "10.15.21.220",
    #    "10.15.21.208",
    #    "10.15.21.212",
    #    "10.15.21.204",
    #    "10.15.21.205",
    #    "10.15.21.206",
    #    "10.15.21.216",
    #    "10.15.21.217",
    #    "10.15.21.218",
]
for ip in ips:
    try:
        # card_number matheus = 34382625
        fingerprints = [
            "45270f149d2255461c8070018412016009861581d05b840d82306288124330098a21c3c1ad8b1fc461540c1304e00f8e2c46d03c8809c6f01e8a03c71074891d07a1b2210b48c1238c1b09815d411ec991ada31cca211fe01dcae0369a178b31260b3b0b703a8c1a0be12f0a1ccc313a910c0c912905384c919588220cb1940c310d813588218e31970c3b0f80930b258fb0988b314fc1970729cfd0958a1b116145072a11c0a38b3811e19d903b12904b1517d2d042040e93009789269310a686349340a1883053a0aa8affdd000112233fffcdd0001122334fccdde001122344fcccde001223344fbccde001233444fbbbcde01344455fabbbcd02445555faaaabce3455556f9999abc4566666f99999a95566666f888899866666665888888766666665888877666666655f88777666666555f88776555666555f77765444444455f7665544334445ff6655443333344fff5544333223344fff44433222233f00000000000000000000000000000000000000000000000000000000000000",
            "451e0f14842255462b0150530620c3f001852105215a892e466049891c8711060e0d47d017882ec8104683324850a38719487165911008f171062c091143091f4921539406ca2174031c4ad1581e21cb51a30d04cba070851f8bb03e132a8bc03a8505cbe01308284d21318a3b4d908f8c1b4e1024912acf012e8e374f503b852f50b12b0f3a52619a93355300ae9d289310708d3bd340ab9b229350730afffee000001ffffffdeee000011fffffdeee0001112fffcddee00011223ffccdee000012233bccddee01112333bccccde01123334bbcccde01233444bbbccde01334444bbbbcde12344455bbbccde23455555fbbbcd034555555fbbbbc056665555bbbbbb977766555bbbbaa98877666fbbbbaa99998766fbcbbbaaa999765ffcccbbbaaaa7544fcccccbbbbbd333ffcccccbbbce12200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        ]
        with ArgosSocket(ip) as s:
            d = datetime.today() - timedelta(days=1)
            # response = s.send_command(
            #    SendFingerprints(card_number="12345676", fingerprints=fingerprints)
            # )
            # response = s.send_command(
            #    CaptureFingerprint(card_number="12345676"), timeout=30
            # )
            # response = s.send_command(DeleteFingerprints(card_number="12345676"))
            response = s.send_command(GetEvents(start_date=d))
            print(response.data)

    except (
        exceptions.ConnectTimeout,
        exceptions.SendCommandTimeout,
        exceptions.ResponseParsing,
        exceptions.TooManyCardsRequested,
        exceptions.GenericErrorResponse,
    ) as e:
        logger.warning(e)
