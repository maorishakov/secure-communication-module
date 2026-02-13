import socket
import threading
import queue

from secure_comm.protocol.stream_parser import StreamParser
from secure_comm.protocol.message import Message


class TCPServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def _rx_loop(self, conn: socket.socket, parser: StreamParser, inbox: "queue.Queue[Message]") -> None:
        """
        RX thread:
        - recv bytes from socket
        - feed into StreamParser
        - put complete Message objects into inbox
        """
        while True:
            data = conn.recv(4096)
            if not data:
                # client disconnected
                break

            messages = parser.feed(data)
            for msg in messages:
                inbox.put(msg)

    def _handle_client(self, conn, addr):
        # IMPORTANT: per-connection state (no mixing between clients)
        parser = StreamParser()
        inbox: "queue.Queue[Message]" = queue.Queue()

        with conn:
            # start RX thread for this connection
            rx_thread = threading.Thread(target=self._rx_loop, args=(conn, parser, inbox), daemon=True)
            rx_thread.start()

            # Main thread: consume messages and handle them
            # We keep running while:
            # - RX thread is alive OR
            # - there are still messages left in inbox
            while rx_thread.is_alive() or not inbox.empty():
                try:
                    msg = inbox.get(timeout=0.5)
                except queue.Empty:
                    continue

                print(
                    f"msg: type={msg.msg_type.name} seq={msg.seq} payload_len={len(msg.payload)}"
                )
                print(msg.payload)

        print("client disconnected")

    def start(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self.host, self.port))
            server_sock.listen(1)

            print(f"Listening on {self.host}:{self.port}")

            while True:
                conn, addr = server_sock.accept()
                print(f"Connected by {addr}")

                client_thread = threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True)
                client_thread.start()


