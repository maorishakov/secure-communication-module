from secure_comm.transport.tcp_client import TCPClient
from secure_comm.session.secure_session import SecureSession


def main():
    client = TCPClient("127.0.0.1", 9000)
    client.connect()
    session = SecureSession(client)
    session.handshake_client(timeout_s=3.0)

    print("Handshake OK ✅")

    session.send_data(b"first secure payload")
    session.send_data(b"second secure payload")

    print("Sent 2 DATA messages ✅")

    client.close()


if __name__ == "__main__":
    main()
