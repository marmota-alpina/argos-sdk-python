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
    def __init__(self, raw_response, parse_string=None, original_exception=None):
        self.raw_response = raw_response
        self.parse_string = parse_string
        self.original_exception = original_exception

    def __repr__(self):
        return f"failed to parse response. received {self.raw_response} and tried do parse with string {self.parse_string}. {self.original_exception}"

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


class TooManyCardsRequested(Exception):
    def __init__(self, cards, max_cards):
        self.cards = cards
        self.max_cards = max_cards

    def __repr__(self):
        return f"You've request {self.cards}, but only {self.max_cards} are allowed"

    def __str__(self):
        return self.__repr__()


class GenericErrorResponse(Exception):
    def __init__(self, message_id, error_message):
        self.message_id = message_id
        self.error_message = error_message

    def __repr__(self):
        return f"The biometric reader returned an error for the requested command: {self.message_id}: {self.error_message}"

    def __str__(self):
        return self.__repr__()
