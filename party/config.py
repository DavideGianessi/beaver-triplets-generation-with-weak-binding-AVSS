import os

N = int(os.getenv("N_PARTIES"))
t = (N-1)//4
p = int(os.getenv("MODULUS"))
amount = int(os.getenv("AMOUNT",0))
PARTY_ID = int(os.getenv("PARTY_ID"))
BASE_PORT = int(os.getenv("BASE_PORT",5000))
MAIN = os.getenv("MAIN","test")
GRACE_PERIOD = int(os.getenv("GRACE_PERIOD",10))
