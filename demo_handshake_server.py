from secure_comm.transport.tcp_server import TCPServer


def main():
    server = TCPServer("127.0.0.1", 9000)
    server.start()


if __name__ == "__main__":
    main()
