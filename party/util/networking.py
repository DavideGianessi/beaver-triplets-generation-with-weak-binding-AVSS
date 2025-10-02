import socket
import msgpack
import struct
from queue import Queue
from threading import Thread
from config import ROUTER_HOST,ROUTER_PORT,PARTY_ID

_inbox = Queue()
_sock = None

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


def connect_to_router():
    global _sock
    _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _sock.connect((ROUTER_HOST, ROUTER_PORT))
    Thread(target=_reader, daemon=True).start()

def _reader():
    global _sock
    while True:
        try:
            msg = decode_message(_sock)
            _inbox.put(msg)
        except Exception as e:
            print(f"[party {PARTY_ID}] connection lost:", e)
            break

def send(to, messageid, data):
    msg = {
        "from": PARTY_ID,
        "to": to,
        "messageid": messageid,
        "data": data,
    }
    _sock.sendall(encode_message(msg))


def getnextmessage():
    return _inbox.get()
