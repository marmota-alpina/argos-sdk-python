from .argos_socket import ArgosSocket
from .commands import *


class SDK:
    # codes to command get_quantity
    QT_USERS = "U"
    QT_CARDS = "C"
    QT_FINGERPRINTS = "D"
    QT_MAX_FINGERPRINTS = "TD"

    # to send cards:
    # Given the card_number is unique, UPDATE or INSERT not seems to change anything

    SEND_INSERT = "I"
    SEND_UPDATE = "A"
    SEND_DELETE = "E"  # complete wipe out, be careful
    MASTER_MODE = "6"  # 6 to set master mode.
    NORMAL_MODE = "1"  # 6 to set master mode.

    def __init__(self, address, **args):
        self._socket = ArgosSocket(address, **args)

    def __enter__(self):
        self._socket.connect()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._socket.close()

    def send_command(
        self,
        command: Command,
        tries: int = ArgosSocket.DEFAULT_MAX_TRIES,
        timeout: int = ArgosSocket.DEFAULT_TIMEOUT,
    ):
        """Sends a command to the socket, that will take care of transforming
        it into bytes and adding metadata adhering the protocol. This method
        should not be called by the end user, since probably there's a method in
        this class that prepare and send it to you."""
        return self._socket.send_command(command, tries, timeout)

    def get_timestamp(self, **args):
        return self.send_command(GetTimestamp(), **args)

    def set_timestamp(self, timestamp, **args):
        return self.send_command(SetTimestamp(timestamp=timestamp), **args)

    def get_cards(self, count, start_index, **args):
        return self.send_command(GetCards(count=count, start_index=start_index), **args)

    def get_quantity(self, type, **args):
        return self.send_command(GetQuantity(type=type), **args)

    def send_cards(
        self,
        card_number,
        master=NORMAL_MODE,
        verify_fingerprint=True,
        mode=SEND_INSERT,
        **args
    ):
        return self.send_command(
            SendCards(card_number, master, verify_fingerprint, mode), **args
        )

    def get_fingerprints(self, card_number, **args):
        return self.send_command(GetFingerprints(card_number=card_number), **args)

    def delete_fingerprints(self, card_number, **args):
        return self.send_command(DeleteFingerprints(card_number=card_number), **args)

    def capture_fingerprint(self, card_number, **args):
        return self.send_command(CaptureFingerprint(card_number=card_number), **args)

    def send_fingerprints(self, card_number, fingerprints, **args):
        return self.send_command(
            SendFingerprints(card_number=card_number, fingerprints=fingerprints), **args
        )

    def get_events(self, start_date, end_date=datetime.datetime.now(), **args):
        return self.send_command(
            GetEvents(start_date=start_date, end_date=end_date), **args
        )
