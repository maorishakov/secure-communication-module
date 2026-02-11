from secure_comm.transport.tcp_client import TCPClient
from secure_comm.protocol.message import Message, MessageType
from enum import IntEnum


def main():
    host = "127.0.0.1"
    port = 9000

    tcp_client = TCPClient(host, port)
    msg = Message(msg_type=MessageType.DATA, seq=1, payload=b"hello secure world")

    tcp_client.send_message(msg)


if __name__ == "__main__":
    main()
