from struct import pack, unpack_from

from dispersy.conversion import BinaryConversion
from dispersy.message import DropPacket


class Conversion(BinaryConversion):

    def __init__(self, community):
        super(Conversion, self).__init__(community, "\x02")
        self.define_meta_message(chr(1), community.get_meta_message(u"message"), self._encode_text, self._decode_text)
        self.define_meta_message(chr(2), community.get_meta_message(u"message-user"), self._encode_text, self._decode_text)

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
