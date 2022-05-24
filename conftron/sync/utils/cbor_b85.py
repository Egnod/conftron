import base64

import cbor2


class CBORb85:
    @staticmethod
    def dumps(data, **kwargs):
        return base64.b85encode(cbor2.dumps(data)).decode()

    @staticmethod
    def loads(data: str):
        return cbor2.loads(base64.b85decode(data))
