class ConnectTimeout(Exception):
    def __init__(self, address, port=None, tries=None):
        self.address = address
        self.port = port
        self.tries = tries

    def __repr__(self):
        return f"failed to connect to {self.address}:{self.port}. Gave up after {self.tries} tries"

    def __str__(self):
        return self.__repr__()

class ResponseParsing(Exception):
    def __init__(self, raw_response, parse_string=None):
        self.raw_response = raw_response
        self.parse_string = parse_string
    def __repr__(self):
        return f"failed to parse response. received {self.raw_response} and tried do parse with string {self.parse_string}"
    def __str__(self):
        return self.__repr__()
class SendCommandTimeout(Exception):
    def __init__(self, address, command):
        self.address = address
        self.command = command
    def __repr__(self):
        return f"failed to send command {self.command} to {self.address}. Timeout"
    def __str__(self):
        return self.__repr__()
