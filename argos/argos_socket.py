import socket
import time
from .exceptions import *
import daiquiri

logger = daiquiri.getLogger("ArgosSocket")


class ArgosSocket:
    DEFAULT_PORT = 3000
    DEFAULT_TIMEOUT = 3  # socket timeout (connect included)
    DEFAULT_MAX_TRIES = 5  # how many times the operation should be tried
    DEFAULT_SLEEP_BETWEEN_TRIES = 0.5  # how much to wait between tries.
    BUFFER_SIZE = 2048
    TIMESTAMP_MASK = "%d/%m/%y %H:%M:%S"
    TIMESTAMP_MASK_EVENTS = (
        "%d/%m/%Y %H:%M:%S"
    )  # the protocol neeeds yyyy format just in events messages...

    def __init__(
        self,
        address,
        port=DEFAULT_PORT,
        timeout=DEFAULT_TIMEOUT,
        max_tries=DEFAULT_MAX_TRIES,
        sleep_between_tries=DEFAULT_SLEEP_BETWEEN_TRIES,
    ):
        self.address = address
        self.port = port
        self.timeout = timeout
        self.max_tries = max_tries
        self.sleep_between_tries = sleep_between_tries
        self.tries = 1
        self.socket = self.config_socket()

    def send_command(self, command, tries=DEFAULT_MAX_TRIES, timeout=DEFAULT_TIMEOUT):
        self.socket.settimeout(timeout)
        if tries == 0:
            raise SendCommandTimeout(self.address, command)
        try:
            tries -= 1
            logger.info("Command sent", address=self.address, command=command)
            self.socket.sendall(command.bytes())
            raw_response = self.receive()
            return command.parse_response(raw_response)
        except socket.timeout as e:
            logger.info(
                "Send command timeout, trying again",
                address=self.address,
                command=command,
            )
            time.sleep(self.sleep_between_tries)
            return self.send_command(command, tries)

    def config_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        return s

    def receive(self):
        raw_response = b""
        while True:
            partial_response = self.socket.recv(self.BUFFER_SIZE)
            raw_response += partial_response
            logger.info(
                "got more bytes",
                total_until_now=len(raw_response),
                chunk_size=len(partial_response),
            )
            if self.check_response_integrity(raw_response):
                logger.info(
                    "Response completely received!", total_size=len(raw_response)
                )
                return raw_response

    @staticmethod
    def check_response_integrity(raw_response):
        return raw_response[0] == 0x02 and raw_response[-1] == 0x03

    def connect(self):
        self.socket = self.config_socket()
        try:
            self.socket.connect((self.address, self.port))
            self.tries = 1
            logger.info("Socket connected", address=self.address)
        except socket.timeout as e:
            if self.tries < self.max_tries:
                logger.info(
                    "Connection Timeout",
                    address=self.address,
                    try_number=self.tries,
                    retry_after=self.sleep_between_tries,
                    max_tries=self.max_tries,
                )
                self.tries += 1
                time.sleep(self.sleep_between_tries)
                self.connect()
            else:
                raise ConnectTimeout(self.address, self.port, self.tries)
                self.tries = 0

    def close(self):
        self.socket.close()
