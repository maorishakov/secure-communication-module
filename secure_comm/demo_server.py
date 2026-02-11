from secure_comm.transport.tcp_server import TCPServer


def main():
    host = "127.0.0.1"
    port = 9000

    TCPServer(host, port).start()


if __name__ == "__main__":
    main()
