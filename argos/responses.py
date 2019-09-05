from parse import compile, search, findall, parse
from .exceptions import *
import daiquiri

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
        "63": "Invalid option",
    }

    def __init__(self, raw_response):
        self.raw_response = raw_response
        self.data = self.parse(raw_response)
        self.verify_response()

    def parse(self, raw_response, **extra_fields):
        return self._parse(raw_response, **extra_fields)

    def _parse(self, raw_response, **extra_fields):
        self.default_response_mapping.update(self.response_mapping)
        result = {}
        for field, (start, end, as_hex) in self.default_response_mapping.items():
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
        status_value = int(self.data.get("message_status"))
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


class SetTimestamp(Response):
    response_mapping = {}


class GetCards(Response):
    response_mapping = {
        "payload": (15, -3, False),
        "response_id": (3, 13, False),
        "message_status": (11, 13, False),
    }

    def __init__(self, raw_response, count):
        self.count = count
        self.raw_response = raw_response
        super().__init__(raw_response)

    def parse_payload(self, bytes):
        results = []
        print(bytes)
        response = findall(
            "[{card_number}[[[[{is_master}[{verify_fingerprint}[[[[[[[[[[",
            bytes.decode(),
        )
        for i in response:
            results.append(i.named)
        return results


class GetQuantity(Response):
    message_id_ok = "01+RQ+00"

    def find_parse_string(self):
        checksum_byte = self.checksum_byte(self.raw_response)
        checksum_hex_string = self.bytes_to_hex_string(checksum_byte)
        return (
            "02{size:2x}00{message_id:16}2b{type}5d{quantity}"
            + checksum_hex_string
            + "03"
        )


class SendCards(Response):
    parse_string = "02{size:2x}00{message_id:30}03"
    message_id_ok = "01+ECAR+00+1+01"


class GetFingerprints(Response):
    parse_string = "02{size:02x}{index:2x}3031{message_id}5d{card_number}7d{count}7d{fingerprints}e103"
    message_id_ok = "+RD+00+D"
    FINGERPRINT_TEMPLATE_SIZE = 768

    def _parse(self, raw_response, **extra_fields):
        message_result = super()._parse(raw_response, **extra_fields)
        raw_fingerprints = message_result["fingerprints"]
        message_result["fingerprints"] = []
        count = message_result["count"]
        print(self.fingerprint_parse_string(count))
        response = parse(self.fingerprint_parse_string(count), raw_fingerprints).named
        for index, fingerprint in response.items():
            message_result["fingerprints"].append(fingerprint)
        print(len(message_result["fingerprints"]))
        return message_result

    def fingerprint_parse_string(self, count, size=FINGERPRINT_TEMPLATE_SIZE):
        parse_string = ""
        for template_index in range(int(count)):
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
