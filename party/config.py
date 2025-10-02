import os

N = int(os.getenv("N", 41))
t = (n-1)//4
PARTY_ID = int(os.getenv("PARTY_ID", -1))
ROUTER_HOST = os.getenv("ROUTER_HOST", "router")
ROUTER_PORT = int(os.getenv("ROUTER_PORT", 9000))
MAIN = os.getenv("MAIN","test")
