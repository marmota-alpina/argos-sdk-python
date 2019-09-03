from parse import compile
from .exceptions import *


class Response:
    parse_string = ""

    def __init__(self, raw_response):
        self.raw_response = raw_response
        self.data = self.parse(raw_response)

    def parse(self, raw_response, **extra_fields):
        try:
            return self._parse(raw_response, **extra_fields)
        except Exception as e:
            raise ResponseParsing(raw_response, self.parse_string)

    def _parse(self, raw_response, **extra_fields):
        raise NotImplemented()

    def __repr__(self):
        return repr(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        return self.data[key]

    def status(self):
        return False


class GetTimestamp(Response):
    parse_string = "02{size:2x}00{message_id:16}2b{timestamp}5d30302f30302f30305d30302f30302f3030{checksum:2x}03"

    def _parse(self, raw_response, **extra_fields):
        p = compile(self.parse_string)
        result = p.parse(raw_response.hex()).named
        for key, value in result.items():
            if not isinstance(value, int):  # ints are already parsed
                result[key] = bytes.fromhex(value).decode("utf-8")  # convert to utf8
        return result

    def status(self):
        return self.data.get("message_id", "") == "01+RH+00"


class SetTimestamp(Response):
    parse_string = "02{size:2x}00{message_id:16}{checksum:2x}03"

    def _parse(self, raw_response, **extra_fields):
        p = compile(self.parse_string)
        result = p.parse(raw_response.hex()).named
        for key, value in result.items():
            if not isinstance(value, int):  # ints are already parsed
                result[key] = bytes.fromhex(value).decode("utf-8")  # convert to utf8
        return result

    def status(self):
        return self.data.get("message_id", "") == "01+EH+00"
