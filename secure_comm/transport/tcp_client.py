import socket
from secure_comm.protocol.message import Message, MessageType
from secure_comm.protocol.framing import encode_message


class TCPClient:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def send_message(self, msg: Message) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            frame = encode_message(msg)
            client_socket.sendall(frame)  # Data must be encoded to bytes
            print(f"Sent: {msg}")



