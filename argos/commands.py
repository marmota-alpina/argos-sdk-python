from .responses import GetTimestamp as TimestampResponse
from .responses import SetTimestamp as SetTimestampResponse
from .responses import GetCards as GetCardsResponse
from .responses import GetQuantity as GetQuantityResponse
from .responses import SendCards as SendCardsResponse
from .responses import GetFingerprints as GetFingerprintsResponse
from .responses import CaptureFingerprint as CaptureFingerprintResponse
from .responses import SendFingerprints as SendFingerprintsResponse
from .responses import GetEvents as GetEventsResponse
from .responses import Response
from .exceptions import *
from .argos_socket import ArgosSocket
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
        MESSAGE_SIZE = Quantidade de bytes da payload, dois bytes. o menos significativo fica
        à esquerda, contrariando o padrão. Por ex uma mensagem com payload 421 bytes ficaria
        com o size A5 01.
        CHECKSUM = Representa a integridade da mensagem (ver método self.checksum())
        END_BYTE = Indifica o fim da transmissão, default 0x00

        Todos os valores são representados em uma string hexadecimal, sem separadores.
        A string é convertida para um bytearray ao final do processo, pelo socket.
        """
        payload = self.payload()  # método implementado por cada command
        payload_size = self.payload_size(
            payload
        )  # hexa com a garantia do "0" na frente
        if not isinstance(payload, bytes):
            payload = payload.encode()
        payload_hex = payload.hex()
        start_hex = f"{Command.BYTE_INIT}{payload_size}"
        checksum_hex = self.checksum(start_hex, payload_hex)
        end_hex = f"{checksum_hex}{Command.BYTE_END}"
        return f"{start_hex}{payload_hex}{end_hex}"

    @staticmethod
    def checksum(start_hex, text_hex):
        byte_array = bytearray.fromhex(start_hex + text_hex)
        checksum_byte = byte_array[1]
        for byte in byte_array[2:]:
            checksum_byte = checksum_byte ^ byte
        checksum_byte = checksum_byte & 0xFF
        return f"{checksum_byte:02X}"

    @staticmethod
    def payload_size(payload):
        hex_size = f"{len(payload):02X}".zfill(4)
        str_chunk_size = int(len(hex_size) / 2)
        firstbyte, secondbyte = (
            hex_size[:str_chunk_size],
            hex_size[str_chunk_size:],
        )  # the protocol says the most significant byte should come after (??)
        return secondbyte + firstbyte


class GetTimestamp(Command):
    response = TimestampResponse

    def payload(self):
        return "01+RH+00"


class SetTimestamp(Command):
    response = SetTimestampResponse

    def __init__(self, timestamp=datetime.datetime.now()):
        self.timestamp = timestamp

    def payload(self):
        timestamp_string = self.timestamp.strftime(ArgosSocket.TIMESTAMP_MASK)
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


class GetQuantity(Command):
    response = GetQuantityResponse

    def __init__(self, type):
        self.type = type

    def payload(self):
        return f"01+RQ+00+{self.type}"

    def parse_response(self, raw_response):
        return self.response(raw_response)


class SendCards(Command):
    response = SendCardsResponse

    def __init__(self, card_number, master, verify_fingerprint, mode):
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


class DeleteFingerprints(Command):
    response = GetFingerprintsResponse

    def __init__(self, card_number):
        self.card_number = card_number

    def payload(self):
        return f"01+ED+00+E]{self.card_number}"


class CaptureFingerprint(Command):
    response = CaptureFingerprintResponse

    def __init__(self, card_number):
        self.card_number = card_number

    def payload(self):
        return f"01+CB+00+{self.card_number}"


class SendFingerprints(Command):
    response = SendFingerprintsResponse

    def __init__(self, card_number, fingerprints):
        self.fingerprints = fingerprints
        self.card_number = card_number

    def payload(self):
        fingerprints = self.fingerprints
        count = len(fingerprints)
        start = f"01+ED+00+D]{self.card_number}{'}'}{count}{'}'}"
        command = start.encode()
        for findex in range(count):
            fingerprint = fingerprints[findex]
            command += f"{findex}{'{'}".encode()
            command += bytearray.fromhex(fingerprint)
        return command


class GetEvents(Command):

    response = GetEventsResponse

    def __init__(self, start_date, end_date, count=50):
        self.start_date = start_date
        self.end_date = end_date
        self.count = count

    def payload(self):
        start_string = self.start_date.strftime(ArgosSocket.TIMESTAMP_MASK_EVENTS)
        end_string = self.end_date.strftime(ArgosSocket.TIMESTAMP_MASK_EVENTS)
        message = f"01+RR+00+D]{self.count}]{start_string}]{end_string}"
        return message
