from protocols.test_protocol import TestProtocol
from protocols.test_sub import TestSub
from protocols.bracha import Bracha
from protocols.main import Main
from protocols.packed_vss import PackedVSS
from protocols.wbavss import WBAVSS
from protocols.verifiable_triple_sharing import TripleSharing

PROTOCOLS = {
    "test": TestProtocol,
    "testsub": TestSub,
    "bracha": Bracha,
    "main": Main,
    "packed_vss": PackedVSS,
    "wbavss": WBAVSS,
    "triple_sharing": TripleSharing,
}
