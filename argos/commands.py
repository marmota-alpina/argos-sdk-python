from .responses import GetTimestamp as TimestampResponse
from .responses import SetTimestamp as SetTimestampResponse
from .responses import GetCards as GetCardsResponse
from .responses import GetQuantity as GetQuantityResponse
from .responses import SendCards as SendCardsResponse
from .responses import GetFingerprints as GetFingerprintsResponse
from .responses import Response
from .exceptions import *

import datetime


class Command:
    BYTE_INIT = "02"
    BYTE_END = "03"
    BYTE_START_MESSAGE = "00"

    response = Response

    def payload(self):
        return ""

    def bytes(self):
        message = self.message()
        return bytearray.fromhex(message)

    def parse_response(self, raw_response):
        return self.response(raw_response)

    def __repr__(self):
        return self.__class__.__name__

    def message(self):
        """
        A mensagem vai no formato:
        INIT_BYTE + MESSAGE_SIZE + BYTE_START_MESSAGE + MESSAGE + CHECKSUM + END_BYTE

        INIT_BYTE = Identifica o início da transmissão, default 0x02
        MESSAGE_SIZE = Quantidade de bytes da payload
        BYTE_START_MESSAGE = Inicializa a payload, default 0x00
        CHECKSUM = Representa a integridade da mensagem (ver método self.checksum())
        END_BYTE = Indifica o fim da transmissão, default 0x00

        Todos os valores são representados em uma string hexadecimal, sem separadores.
        A string é convertida para um bytearray ao final do processo, pelo socket.
        """
        payload = self.payload()  # método implementado por cada command
        payload_size = f"{len(payload):02X}"  # hexa com a garantia do "0" na frente
        payload_hex = payload.encode().hex()
        start_hex = f"{Command.BYTE_INIT}{payload_size}{Command.BYTE_START_MESSAGE}"
        checksum_hex = self.checksum(start_hex, payload_hex)
        end_hex = f"{checksum_hex}{Command.BYTE_END}"
        return f"{start_hex}{payload_hex}{end_hex}"

    @staticmethod
    def checksum(start_hex, text_hex):
        byte_array = bytearray.fromhex(start_hex + text_hex)
        checksum_byte = byte_array[1]
        for byte in byte_array[2:]:
            checksum_byte = checksum_byte ^ byte
        return f"{checksum_byte:02X}"


class GetTimestamp(Command):
    response = TimestampResponse

    def payload(self):
        return "01+RH+00"


class SetTimestamp(Command):
    response = SetTimestampResponse
    timestamp_mask = "%d/%m/%y %H:%M:%S"

    def __init__(self, timestamp=datetime.datetime.now()):
        self.timestamp = timestamp

    def payload(self):
        timestamp_string = self.timestamp.strftime(self.timestamp_mask)
        message = f"01+EH+00+{timestamp_string}]00/00/00]00/00/00"
        return message


class GetCards(Command):
    response = GetCardsResponse
    MAX_CARDS = 30

    def __init__(self, count, start_index):
        if count > self.MAX_CARDS:
            raise TooManyCardsRequested(count, self.MAX_CARDS)
        self.count = count
        self.start_index = start_index

    def payload(self):
        return f"01+RCAR+00+{self.count}]{self.start_index}"

    def parse_response(self, raw_response):
        return self.response(raw_response, self.count)


class GetQuantity(Command):
    response = GetQuantityResponse
    USERS = "U"
    CARDS = "C"
    FINGERPRINTS = "D"
    MAX_FINGERPRINTS = "TD"

    def __init__(self, type):
        self.type = type

    def payload(self):
        return f"01+RQ+00+{self.type}"

    def parse_response(self, raw_response):
        return self.response(raw_response)


class SendCards(Command):
    response = SendCardsResponse
    """ Given the card_number is unique, UPDATE or INSERT not seems to change anything """
    SEND_INSERT = "I"
    SEND_UPDATE = "A"
    SEND_DELETE = "E"  # complete wipe out, be careful
    MASTER_MODE = "1"  # 6 to set master mode.

    def __init__(
        self, card_number, master=MASTER_MODE, verify_fingerprint=True, mode=SEND_INSERT
    ):
        self.card_number = card_number
        self.master = master
        self.verify_fingerprint = verify_fingerprint
        self.mode = mode

    def payload(self):
        message = f"01+ECAR+00+1+{self.mode}[1[{self.card_number}[[[[{self.master}[{self.verify_fingerprint:d}[[[[[[[[[["
        return message


class GetFingerprints(Command):
    response = GetFingerprintsResponse

    def __init__(self, card_number):
        self.card_number = card_number

    def payload(self):
        return f"01+RD+00+D]{self.card_number}"
