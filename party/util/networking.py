import socket
import msgpack
import struct
from queue import Queue
from threading import Thread
from config import PARTY_ID,N,BASE_PORT
from util.logging import log_traffic
import time

PORT=BASE_PORT+PARTY_ID

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
            msg={"messageid":decode_id(msg[0]),"from":msg[1],"to":msg[2],"data":msg[3]}
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
    server_sock.bind(("127.0.0.1", PORT))
    server_sock.listen()
    Thread(target=_accept_loop, args=(server_sock,), daemon=True).start()

    time.sleep(0.2)  # small delay to ensure listener is active

    # Outgoing connections: connect to parties with smaller IDs
    for other in range(1, PARTY_ID):
        host = f"127.0.0.1"
        other_port = BASE_PORT + other
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, other_port))
                _connections[other] = sock
                Thread(target=_reader, args=(sock,), daemon=True).start()
                handshake = [
                    encode_id("__connect__"),
                    PARTY_ID,
                    other,
                    b"",
                    ]
                sock.sendall(encode_message(handshake))
                break
            except Exception:
                time.sleep(0.2)

    print(f"[party {PARTY_ID}] All outgoing connections established.")

def send(to, messageid, data):
    msg = [
        encode_id(messageid),
        PARTY_ID,
        to,
        data,
        ] 
    encoded=encode_message(msg)
    log_traffic(messageid, PARTY_ID, to, len(encoded))
    _connections[to].sendall(encoded)


def getnextmessage():
    return _inbox.get()

#temporary
def encode_id(messagepath):
    if messagepath=="__connect__":
        return 0
    myid=0
    protocols=messagepath.split("/")[1:]
    if protocols[1]=="packed_vss_0":
        myid+=1000000
    if protocols[1]=="wbavss_0":
        myid+=2000000
    if len(protocols)==4:
        myid+=10*(1+int(protocols[2].split("_")[-1]))
    messages={"shares":1,"exchange":2,"reconstruct":3,"init":4,"echo":5,"ready":6}
    myid+=messages[protocols[-1]]
    return myid
def decode_id(myid):
    if myid==0:
        return "__connect__"
    messages=["","shares","exchange","reconstruct","init","echo","ready"]
    path="/"+messages[myid%10]
    myid=myid//10
    if myid%100000:
        path=f"/bracha_{(myid%100000)-1}"+path
    myid=myid//100000
    if myid==1:
        path=f"/packed_vss_0"+path
    if myid==2:
        path=f"/wbavss_0"+path
    path=f"/triple_sharing_0"+path
    return path

