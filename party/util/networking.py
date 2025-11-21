import socket
import msgpack
import struct
from queue import Queue
from threading import Thread
from config import PARTY_ID,N
from util.logging import log_traffic
import time

PORT=5000

_inbox = Queue()
_connections = {}
_known_senders = set()


def encode_message(msg: dict) -> bytes:
    packed = msgpack.packb(msg, use_bin_type=True)
    return struct.pack("!I", len(packed)) + packed

def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket closed unexpectedly")
        buf += chunk
    return buf

def decode_message(sock: socket.socket) -> dict:
    raw_len = recv_exact(sock, 4)
    length, = struct.unpack("!I", raw_len)
    raw_data = recv_exact(sock, length)
    msg = msgpack.unpackb(raw_data, raw=False)
    return msg

def _accept_loop(server_sock):
    while True:
        conn, _ = server_sock.accept()
        Thread(target=_reader, args=(conn,), daemon=True).start()

def _reader(sock):
    while True:
        try:
            msg = decode_message(sock)
            sender = msg["from"]
            if sender not in _connections:
                _connections[sender] = sock
                _known_senders.add(sender)
            _inbox.put(msg)
        except Exception as e:
            print(f"[party {PARTY_ID}] connection lost:", e)
            break

def start_network():
    """Create:
       - a server socket (to accept connections from higher ID parties)
       - outgoing connections (to lower ID parties)
    """
    global _connections

    # Start server socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("0.0.0.0", PORT))
    server_sock.listen()
    Thread(target=_accept_loop, args=(server_sock,), daemon=True).start()

    time.sleep(0.2)  # small delay to ensure listener is active

    # Outgoing connections: connect to parties with smaller IDs
    for other in range(1, PARTY_ID):
        host = f"party{other}"
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, PORT))
                _connections[other] = sock
                Thread(target=_reader, args=(sock,), daemon=True).start()
                handshake = {
                    "from": PARTY_ID,
                    "to": other,
                    "messageid": "__connect__",
                    "data": b"",
                }
                sock.sendall(encode_message(handshake))
                break
            except Exception:
                time.sleep(0.2)

    print(f"[party {PARTY_ID}] All outgoing connections established.")

def send(to, messageid, data):
    msg = {
        "from": PARTY_ID,
        "to": to,
        "messageid": messageid,
        "data": data,
    } 
    encoded=encode_message(msg)
    log_traffic(messageid, PARTY_ID, to, len(encoded))
    _connections[to].sendall(encoded)


def getnextmessage():
    return _inbox.get()
