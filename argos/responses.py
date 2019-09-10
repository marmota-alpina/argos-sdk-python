from parse import compile, search, findall, parse
from .exceptions import *
import daiquiri
from .argos_socket import ArgosSocket
import time

logger = daiquiri.getLogger("Responses")


class Response:
    parse_string = ""
    default_response_mapping = {
        "size": (1, 2, True),
        "index": (2, 3, True),
        "response_id": (3, 11, False),
        "message_status": (9, 11, False),
        "checksum": (-3, -1, True),
    }
    error_messages = {
        "00": "No errors",
        "10": "Unknown command",
        "11": "Invalid package size",
        "26": "Fingerprint index not found",
        "29": "Could not capture or understand a fingerprint",
        "37": "Invalid card reference",
        "63": "Invalid option",
    }

    def __init__(self, raw_response):
        self.raw_response = raw_response
        self.data = self.parse(raw_response)
        self.verify_response()

    def parse(self, raw_response, **extra_fields):
        return self._parse(raw_response, **extra_fields)

    def _parse(self, raw_response, **extra_fields):
        response_mapping = dict(self.default_response_mapping, **self.response_mapping)
        result = {}
        for field, (start, end, as_hex) in response_mapping.items():
            bytes = raw_response[start:end]
            if field is "payload":
                value = self.parse_payload(bytes)
            elif as_hex:
                value = bytes.hex()
            else:
                value = bytes.decode()
            result[field] = value
        return result

    def parse_payload(self, bytes):
        return bytes.decode()

    def status(self):
        try:
            status_value = int(self.data.get("message_status"))
        except Exception as e:
            status_value = 9999
        return status_value < 10

    def error_message(self):
        message_status = self.data.get("message_status")
        return self.error_messages.get(message_status, "Unknown")

    def verify_response(self):
        if not self.status():
            raise GenericErrorResponse(
                self.data.get("response_id", "UNKNOWN"), self.error_message()
            )

    def find_parse_string(self):
        return self.parse_string

    @staticmethod
    def find_message_index(count):
        return "0" + str(int(count // 10))

    def __repr__(self):
        if self.data.get("payload") is not None:
            return repr(self.data["payload"])
        return repr(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        return self.data[key]

    @staticmethod
    def string_to_hex_string(ascii_string):
        hex_string = ""
        for char in ascii_string:
            hex_string += "{:02x}".format(ord(char))
        return hex_string

    @staticmethod
    def bytes_to_hex_string(bytes):
        hex_string = ""
        for byte in bytes:
            hex_string += "{:02x}".format(byte)
        return hex_string

    @staticmethod
    def checksum_byte(raw_response):
        return raw_response[-2:-1]


class GetTimestamp(Response):
    response_mapping = {"payload": (12, 29, False)}

    def parse_payload(self, bytes):
        string = bytes.decode()
        return time.strptime(string, ArgosSocket.TIMESTAMP_MASK)


class SetTimestamp(Response):
    response_mapping = {}


class GetCards(Response):
    response_mapping = {
        "payload": (15, -3, False),
        "response_id": (3, 13, False),
        "message_status": (11, 13, False),
    }

    def parse_payload(self, bytes):
        results = []
        response = findall(
            "[{card_number}[[[[{is_master}[{verify_fingerprint}[[[[[[[[[[",
            bytes.decode(),
        )
        for i in response:
            results.append(i.named)
        return results


class GetQuantity(Response):
    response_mapping = {"payload": (14, -2, True), "type": (12, 13, False)}


class SendCards(Response):
    response_mapping = {
        "response_id": (3, 13, False),
        "message_status": (11, 13, False),
    }


class GetFingerprints(Response):
    response_mapping = {"payload": (23, -2, False)}
    FINGERPRINT_TEMPLATE_SIZE = 768

    def parse_payload(self, bytes):
        if len(bytes) == 0:
            return
        result = []
        count = int(bytes[0:1])
        raw_hex_fingerprints = bytes.hex()
        fingerprints = parse(self.fingerprint_parse_string(count), raw_hex_fingerprints)
        for index, fingerprint in fingerprints.named.items():
            result.append(fingerprint)
        return result

    def fingerprint_parse_string(self, count: int, size=FINGERPRINT_TEMPLATE_SIZE):
        parse_string = "{}"
        for template_index in range(count):
            template_index_hex = self.string_to_hex_string(str(template_index))
            parse_string += (
                template_index_hex
                + "7b{fingerprint"
                + str(template_index)
                + ":"
                + str(size)
                + "}"
            )
        return parse_string


class CaptureFingerprint(Response):
    response_mapping = {}


class SendFingerprints(Response):
    response_mapping = {}


class GetEvents(Response):
    response_mapping = {"count": (12, 14, False), "payload": (15, -2, False)}

    def parse_payload(self, bytes):
        results = []
        response = findall(
            "{index}[{type}[{card_number}[{timestamp}[{direction}[{is_master}[{reader_id}",
            bytes.decode(),
        )
        for i in response:
            results.append(i.named)
        return results
