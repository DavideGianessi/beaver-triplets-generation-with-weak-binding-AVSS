from protocols.test_protocol import TestProtocol
from protocols.test_sub import TestSub
from protocols.bracha import Bracha
from protocols.main import Main

PROTOCOLS = {
    "test": TestProtocol,
    "testsub": TestSub,
    "bracha": Bracha,
    "main": Main,
}
