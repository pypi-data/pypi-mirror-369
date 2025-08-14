class PrivateKey(object):
    """私钥对象"""

    def __init__(self, private_key):
        self.private_key = private_key

    def private_bytes(self) -> bytes:
        pass

    def public_bytes(self) -> bytes:
        pass


class X509Certificate(object):
    """证书对象"""

    def __init__(self, certificate):
        self.certificate = certificate

    def serial_number(self):
        pass

    def public_bytes(self):
        pass
