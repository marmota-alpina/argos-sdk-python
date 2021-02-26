class ConnectTimeout(Exception):
    def __init__(self, address, port=None, tries=None):
        self.address = address
        self.port = port
        self.tries = tries
        super().__init__(address)

    def __repr__(self):
        return f"failed to connect to {self.address}:{self.port}. Gave up after {self.tries} tries"

    def __str__(self):
        return self.__repr__()


class SendCommandTimeout(Exception):
    def __init__(self, address, command):
        self.address = address
        self.command = command
        super().__init__(address)

    def __repr__(self):
        return f"failed to send command {self.command} to {self.address}. Timeout"

    def __str__(self):
        return self.__repr__()


class TooManyCardsRequested(Exception):
    def __init__(self, cards, max_cards):
        self.cards = cards
        self.max_cards = max_cards
        super().__init__(cards)

    def __repr__(self):
        return f"You've request {self.cards}, but only {self.max_cards} are allowed"

    def __str__(self):
        return self.__repr__()


class GenericErrorResponse(Exception):
    def __init__(self, message_id, error_message):
        self.message_id = message_id
        self.error_message = error_message
        super().__init__(error_message)

    def __repr__(self):
        return f"The biometric reader returned an error: {self.message_id}: {self.error_message}"

    def __str__(self):
        return self.__repr__()
