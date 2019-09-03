from parse import compile, search, findall
from .exceptions import *


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
        p = compile(self.find_parse_string())
        result = p.parse(raw_response.hex()).named
        for key, value in result.items():
            if not isinstance(value, int):  # ints are already parsed
                result[key] = bytes.fromhex(value).decode()
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
        index = self.find_message_index(self.count)
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
