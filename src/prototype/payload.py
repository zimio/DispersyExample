from dispersy.payload import Payload


class SyncPayload(Payload):

    class Implementation(Payload.Implementation):

        def __init__(self, meta, digest):
            super(SyncPayload.Implementation, self).__init__(meta)
            self._digest = digest

        @property
        def digest(self):
            return self._digest

class InterestPayload(Payload):

    class Implementation(Payload.Implementation):

        def __init__(self, meta, producer, seq_number):
            super(InterestPayload.Implementation, self).__init__(meta)
            self._seq_number = seq_number
            self._producer = producer

        @property
        def seq_number(self):
            return self._seq_number

        @property
        def producer(self):
            return self._producer



class DataPayload(Payload):

    class Implementation(Payload.Implementation):

        def __init__(self, meta, text):
            assert isinstance(text, unicode)
            assert len(text.encode("UTF-8")) <= 255
            super(DataPayload.Implementation, self).__init__(meta)
            self._text = text

        @property
        def text(self):
            return self._text

