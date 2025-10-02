import socket
import struct
import msgpack
import select
import os

# --- Config ---
N_PARTIES = int(os.environ.get("N_PARTIES", 41))
ROUTER_HOST = "0.0.0.0"
ROUTER_PORT = 9000

OUTPUT_FOLDER = "/outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
log_path = os.path.join(OUTPUT_FOLDER, "router.txt")
if os.path.exists(log_path):
    try:
        os.remove(log_path)
    except OSError as e:
        print(f"Error deleting old log file {path}: {e}")

# --- Helpers for encoding/decoding ---
def encode_message(msg: dict) -> bytes:
    packed = msgpack.packb(msg, use_bin_type=True)
    return struct.pack("!I", len(packed)) + packed

def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket closed")
        buf += chunk
    return buf

def decode_message(sock: socket.socket) -> dict:
    raw_len = recv_exact(sock, 4)
    (length,) = struct.unpack("!I", raw_len)
    raw_data = recv_exact(sock, length)
    return msgpack.unpackb(raw_data, raw=False)

def log(*args):
    with open(log_path, "a") as f:
        print(*args, file=f)

# --- Router main ---
def main():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((ROUTER_HOST, ROUTER_PORT))
    listener.listen(N_PARTIES)
    log(f"Router listening on {ROUTER_HOST}:{ROUTER_PORT}")

    connections = {}  # party_id -> socket
    sockets = [listener]

    while True:
        ready, _, _ = select.select(sockets, [], [])
        for sock in ready:
            if sock is listener:
                conn, addr = listener.accept()
                ip = addr[0]
                try:
                    # Take last two octets: 172.20.A.B -> (A * 256 + B)
                    parts = ip.split(".")
                    last_two = int(parts[2]) * 256 + int(parts[3])
                    party_id = last_two - 10
                except Exception:
                    log(f"Invalid IP format for {ip}, closing.")
                    conn.close()
                    continue

                if party_id in connections:
                    log(f"Duplicate connection for party {party_id}, closing new one.")
                    conn.close()
                    continue

                connections[party_id] = conn
                sockets.append(conn)
                log(f"Connected party {party_id} from {ip}")

            else:
                try:
                    msg = decode_message(sock)
                except Exception as e:
                    # Drop connection on error/disconnect
                    pid = next((pid for pid, cs in connections.items() if cs == sock), None)
                    if pid is not None:
                        log(f"Party {pid} disconnected: {e}")
                        sockets.remove(sock)
                        del connections[pid]
                    sock.close()
                    # If all parties disconnected, exit
                    if not connections:
                        log("All parties disconnected, router exiting.")
                        return
                    continue

                log(msg)

                dest = msg.get("to")
                if dest in connections:
                    try:
                        encoded_msg=encode_message(msg)
                        connections[dest].sendall(encoded_msg)
                    except Exception as e:
                        log(f"Failed to forward to {dest}: {e}")

if __name__ == "__main__":
    main()
