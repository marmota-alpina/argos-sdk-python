class Command:
    BYTE_INIT = "02"
    BYTE_END = "03"
    BYTE_START_MESSAGE = "00"

    def payload(self):
        return ""

    def bytes(self):
        message = self.message()
        return bytearray.fromhex(message)

    def message(self):
        """
        A mensagem vai no formato:
        INIT_BYTE + MESSAGE_SIZE + BYTE_START_MESSAGE + MESSAGE + CHECKSUM + END_BYTE

        INIT_BYTE = Identifica o início da transmissão, default 0x02
        MESSAGE_SIZE = Quantidade de bytes da payload
        BYTE_START_MESSAGE = Inicializa a payload, default 0x00
        CHECKSUM = Representa a integridade da mensagem (ver método self.checksum())
        END_BYTE = Indifica o fim da transmissão, default 0x00

        Todos os valores são representados em uma string hexadecimal, sem separadores.
        A string é convertida para um bytearray ao final do processo, pelo socket.
        """
        payload = self.payload()  # método implementado por cada command
        payload_size = f"{len(payload):02X}"  # hexa com a garantia do "0" na frente
        payload_hex = payload.encode().hex()
        start_hex = f"{Command.BYTE_INIT}{payload_size}{Command.BYTE_START_MESSAGE}"
        checksum_hex = self.checksum(start_hex, payload_hex)
        end_hex = f"{checksum_hex}{Command.BYTE_END}"
        return f"{start_hex}{payload_hex}{end_hex}"

    @staticmethod
    def checksum(start_hex, text_hex):
        byte_array = bytearray.fromhex(start_hex + text_hex)
        checksum_byte = byte_array[1]
        for byte in byte_array[2:]:
            checksum_byte = checksum_byte ^ byte
        return f"{checksum_byte:02X}"


class GetTimestamp(Command):
    def payload(self):
        return "01+RH+00"
