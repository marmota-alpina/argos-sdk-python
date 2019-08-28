class ConnectTimeout(Exception):
    def __init__(self, address, port=None, tries=None):
        self.address = address
        self.port = port
        self.tries = tries

    def __repr__(self):
        return f"failed to connect to {self.address}:{self.port}. Gave up after {self.tries} tries"

    def __str__(self):
        return self.__repr__()
        
class SendCommandTimeout(Exception):
    pass
