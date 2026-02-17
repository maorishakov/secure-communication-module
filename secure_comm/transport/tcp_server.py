import socket
import threading
import queue

from secure_comm.protocol.framing import encode_message
from secure_comm.protocol.stream_parser import StreamParser
from secure_comm.protocol.message import Message, MessageType


class TCPServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._stop = threading.Event()

    def stop(self) -> None:
        self._stop.set()

    def _rx_loop(self, conn: socket.socket, parser: StreamParser, inbox: "queue.Queue[Message]") -> None:
        """
        RX thread:
        - recv bytes from socket
        - feed into StreamParser
        - put complete Message objects into inbox
        """
        conn.settimeout(0.5)

        while not self._stop.is_set():
            try:
                data = conn.recv(4096)
            except socket.timeout:
                continue
            except OSError:
                break

            if not data:
                break

            try:
                messages = parser.feed(data)
            except Exception as e:
                print(f"Parser error: {e}")
                break

            for msg in messages:
                inbox.put(msg)

    def send(self, conn: socket.socket, msg: Message):
        # if not self._connected:
        #     raise RuntimeError("Client not connected")

        frame = encode_message(msg)
        conn.sendall(frame)
        print(f"Sent: type={msg.msg_type.name} seq={msg.seq} payload_len={len(msg.payload)}")
        print(f"Payload={msg.payload}")

    def _handle_client(self, conn, addr):
        parser = StreamParser()
        inbox: "queue.Queue[Message]" = queue.Queue()

        with conn:
            rx_thread = threading.Thread(target=self._rx_loop, args=(conn, parser, inbox), daemon=True)
            rx_thread.start()

            while (not self._stop.is_set()) and (rx_thread.is_alive() or not inbox.empty()):
                try:
                    msg = inbox.get(timeout=0.5)
                except queue.Empty:
                    continue

                print(f"msg: type={msg.msg_type.name} seq={msg.seq} payload_len={len(msg.payload)}")
                print(msg.payload)

                if msg.msg_type == MessageType.HANDSHAKE_HELLO:
                    reply_msg = Message(msg_type=MessageType.HANDSHAKE_REPLY, seq=msg.seq, payload=b"")
                    self.send(conn, reply_msg)

        print("client disconnected")

    def start(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self.host, self.port))
            server_sock.listen(50)

            server_sock.settimeout(0.5)

            print(f"Listening on {self.host}:{self.port}")

            try:
                while not self._stop.is_set():
                    try:
                        conn, addr = server_sock.accept()
                    except socket.timeout:
                        continue
                    except OSError:
                        break

                    print(f"Connected by {addr}")
                    client_thread = threading.Thread(
                        target=self._handle_client, args=(conn, addr), daemon=True
                    )
                    client_thread.start()

            except KeyboardInterrupt:
                print("\nStopping server...")
                self.stop()

            print("Server stopped cleanly.")
