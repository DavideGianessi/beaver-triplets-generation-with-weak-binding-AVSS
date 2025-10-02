from util.networking as networking
from protocol_manager import ProtocolManager
from util.logging import log
from config import MAIN

def main():
    networking.connect_to_router()
    manager = ProtocolManager(f"/{MAIN}_0/")
    manager.start_protocol(f"/{MAIN}_0/")
    while not manager.is_done():
        msg = getnextmessage()
        manager.dispatch(msg)
    log(manager.result)

if __name__ == "__main__":
    main()
