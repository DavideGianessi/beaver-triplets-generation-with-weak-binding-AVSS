import os

N = int(os.getenv("N_PARTIES"))
t = (N-1)//4
PARTY_ID = int(os.getenv("PARTY_ID"))
ROUTER_HOST = os.getenv("ROUTER_HOST", "router")
ROUTER_PORT = int(os.getenv("ROUTER_PORT", 9000))
MAIN = os.getenv("MAIN","test")
