import util.networking as networking
from protocol_manager import ProtocolManager
from util.logging import log
from config import MAIN
import time

def main():
    networking.connect_to_router()
    time.sleep(5)
    manager = ProtocolManager(f"/{MAIN}_0/")
    #print(manager.mailbox)
    manager.start_protocol(f"/{MAIN}_0/")
    while not manager.is_done():
        msg = networking.getnextmessage()
        manager.dispatch(msg)
    log(manager.result)

if __name__ == "__main__":
    main()
