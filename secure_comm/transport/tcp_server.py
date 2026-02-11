import socket
from secure_comm.protocol.stream_parser import StreamParser


class TCPServer:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._parser = StreamParser()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.bind((self.host, self.port))
            # support 1 client
            tcp_socket.listen(1)
            print(f"Listening on {self.host}:{self.port}")
            # accept a connection
            conn, addr = tcp_socket.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    messages = self._parser.feed(data)
                    for msg in messages:
                        print(f"msg: type={msg.msg_type.name} seq={msg.seq} payload_len={len(msg.payload)}")
                        print(msg.payload)





