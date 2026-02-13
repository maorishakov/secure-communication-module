from secure_comm.transport.tcp_client import TCPClient
from secure_comm.protocol.message import Message, MessageType
import time


def main():
    host = "127.0.0.1"
    port = 9000

    tcp_client = TCPClient(host, port)
    tcp_client.connect()
    for i in range(1, 8):
        msg = Message(msg_type=MessageType.DATA, seq=i, payload=b"hello secure world")
        tcp_client.send(msg)
        time.sleep(1.5)

    tcp_client.close()


if __name__ == "__main__":
    main()
