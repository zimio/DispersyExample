from dispersy.payload import Payload


class StatusPayload(Payload):

    class Implementation(Payload.Implementation):

        def __init__(self, meta, status):
            super(StatusPayload.Implementation, self).__init__(meta)
            self._status = status

        @property
        def status(self):
            return self._status

class EmptyPayload(Payload):

    class Implementation(Payload.Implementation):

        def __init__(self, meta, foo):
            super(EmptyPayload.Implementation, self).__init__(meta)

class MessagePayload(Payload):

    class Implementation(Payload.Implementation):

        def __init__(self, meta, text):
            assert isinstance(text, unicode)
            assert len(text.encode("UTF-8")) <= 255
            super(MessagePayload.Implementation, self).__init__(meta)
            self._text = text

        @property
        def text(self):
            return self._text

