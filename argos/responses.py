from parse import compile, search, findall, parse
from .exceptions import *
import daiquiri

logger = daiquiri.getLogger("Responses")


class Response:
    parse_string = ""

    def __init__(self, raw_response):
        self.raw_response = raw_response
        self.data = self.parse(raw_response)
        self.verify_response()

    def parse(self, raw_response, **extra_fields):
        try:
            return self._parse(raw_response, **extra_fields)
        except Exception as e:
            raise ResponseParsing(raw_response, self.find_parse_string(), e)

    def _parse(self, raw_response, **extra_fields):
        result = parse(self.find_parse_string(), raw_response.hex()).named
        for key, value in result.items():
            if not isinstance(value, int):  # ints are already parsed
                try:
                    result[key] = bytes.fromhex(value).decode()
                except Exception as e:
                    logger.info("Couldn't decode value", key=key)
                    pass
        return result

    def status(self):
        return self.data.get("message_id", "") == self.message_id_ok

    def verify_response(self):
        if not self.status():
            raise GenericErrorResponse(self.data.get("message_id", "UNKNOWN"))

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
    parse_string = "02{size:2x}00{message_id:16}2b{timestamp}5d30302f30302f30305d30302f30302f3030{checksum:2x}03"
    message_id_ok = "01+RH+00"


class SetTimestamp(Response):
    parse_string = "02{size:2x}00{message_id:16}{checksum:2x}03"
    message_id_ok = "01+EH+00"


class GetCards(Response):
    message_id_ok = "01+RCAR+00"

    def __init__(self, raw_response, count):
        self.count = count
        self.raw_response = raw_response
        self.parse_string = self.find_parse_string()
        super().__init__(raw_response)

    def find_parse_string(self):
        checksum_byte = self.checksum_byte(self.raw_response)
        checksum_hex_string = self.bytes_to_hex_string(checksum_byte)
        return (
            "02{size:2x}{index:02x}{message_id:20}2b"
            + self.string_to_hex_string(str(self.count))
            + "2b{raw_cards}"
            + checksum_hex_string
            + "03"
        )

    def _parse(self, raw_response, **extra_fields):
        message_result = super()._parse(raw_response, **extra_fields)
        message_result["cards"] = []
        response = findall(
            "[{card_number}[[[[{is_master}[{verify_fingerprint}[[[[[[[[[[",
            message_result["raw_cards"],
        )
        for i in response:
            message_result["cards"].append(i.named)
        return message_result


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
