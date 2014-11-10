from struct import pack, unpack_from

from dispersy.conversion import BinaryConversion
from dispersy.message import DropPacket


class Conversion(BinaryConversion):

    def __init__(self, community):
        super(Conversion, self).__init__(community, "\x02")
        self.define_meta_message(chr(1), community.get_meta_message(u"message"), self._encode_text, self._decode_text)
        self.define_meta_message(chr(2), community.get_meta_message(u"message-user"), self._encode_text, self._decode_text)
        self.define_meta_message(chr(3), community.get_meta_message(u"nick"), self._encode_text, self._decode_text)
        self.define_meta_message(chr(4), community.get_meta_message(u"set-nick"), self._encode_text, self._decode_text)

    def _encode_text(self, message):
        assert len(message.payload.text.encode("UTF-8")) < 256
        text = message.payload.text.encode("UTF-8")
        return pack("!B", len(text)), text[:255]

    def _decode_text(self, placeholder, offset, message):
        if len(message) < offset + 1:
            raise DropPacket("Insufficient packet size")

        text_length, = unpack_from("!B", message, offset)
        offset += 1

        try:
            text = message[offset:offset + text_length].decode("UTF-8")
            offset += text_length
        except UnicodeError:
            raise DropPacket("Unable to decode UTF-8")

        return offset, placeholder.meta.payload.implement(text)


class StatusConversion(BinaryConversion):

    def __init__(self, community):
        super(StatusConversion, self).__init__(community, "\x02")
        self.define_meta_message(chr(5), community.get_meta_message(u"status"), self._encode_status, self._decode_status)
        self.define_meta_message(chr(6), community.get_meta_message(u"set-status"), self._encode_status, self._decode_status)

    def _encode_status(self, message):
        assert (message.payload.status < 5)
        status = message.payload.status
        return (pack("H", status),)

    def _decode_status(self, placeholder, offset, message):
        if len(message) < offset + 1:
            raise DropPacket("Insufficient packet size")

        status = unpack_from("H", message, offset)[0]
        offset = offset + 2
        return offset, placeholder.meta.payload.implement(status)

class EmptyConversion(BinaryConversion):

    def __init__(self, community):
        super(EmptyConversion, self).__init__(community, "\x02")
        self.define_meta_message(chr(7), community.get_meta_message(u"get-status"), self._encode_empty, self._decode_empty)
        self.define_meta_message(chr(8), community.get_meta_message(u"get-nick"), self._encode_empty, self._decode_empty)

    def _encode_empty(self, message):
        return ('0',)

    def _decode_empty(self, placeholder, offset, message):
        return (offset + 1, placeholder.meta.payload.implement(0))

