import socket
import time
from .exceptions import *
import daiquiri

logger = daiquiri.getLogger("ArgosSocket")


class ArgosSocket:
    DEFAULT_PORT = 3000
    DEFAULT_TIMEOUT = 2  # socket timeout (connect included)
    DEFAULT_MAX_TRIES = 5  # how many times the operation should be tried
    DEFAULT_SLEEP_BETWEEN_TRIES = 0.5  # how much to wait between tries.

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

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.socket.close()

    def send_command(self, command, tries=DEFAULT_MAX_TRIES):
        if tries == 0:
            raise SendCommandTimeout(self.address, command)
        try:
            tries -= tries
            self.socket.sendall(command.bytes())
            raw_response = self.socket.recv(1024)
            logger.info("Command sent", address=self.address, command=command)
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
