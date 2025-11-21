import util.networking as networking
from protocol_manager import ProtocolManager
from util.logging import log
from config import MAIN,GRACE_PERIOD,PARTY_ID
import time
import threading


def handle_messages(manager):
    while True:
        msg = networking.getnextmessage()
        manager.dispatch(msg)

def main():
    networking.start_network()
    time.sleep(20)
    print(f"|{PARTY_ID}| starting")
    manager = ProtocolManager(f"/{MAIN}_0/")
    manager.start_protocol(f"/{MAIN}_0/")
    while not manager.is_done():
        msg = networking.getnextmessage()
        manager.dispatch(msg)
    log(manager.result)
    print(f"|{PARTY_ID}|protocol finished, waiting {GRACE_PERIOD} seconds for others")

    maintenance = threading.Thread(target = handle_messages,args=(manager,), daemon=True)
    maintenance.start()
    time.sleep(GRACE_PERIOD)


if __name__ == "__main__":
    main()
