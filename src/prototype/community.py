import logging

from .conversion import Conversion
from .payload import MessagePayload
from .digesttree import DigestTree
from .pit import PIT

from dispersy.authentication import MemberAuthentication
from dispersy.community import Community
from dispersy.conversion import DefaultConversion
from dispersy.destination import CommunityDestination
from dispersy.distribution import FullSyncDistribution, LastSyncDistribution, DirectDistribution
from dispersy.message import BatchConfiguration, Message, DelayMessageByProof
from dispersy.resolution import PublicResolution

from twisted.internet.task import LoopingCall


class ExampleCommunity(Community):

    # @property
    # def dispersy_auto_download_master_member(self):
    #     # there is no dispersy-identity for the master member, so don't try to download (???)
    #     return False

    def initialize(self, msg='hmmmMm'):
        "Called After init_community is called"

        super(ExampleCommunity, self).initialize()
        logging.info("ExampleCommunity Initalized")
        self.digesttree = DigestTree(self.my_member.mid)
        self.pit = PIT()
        #self.send_message(msg)

        self.register_task("send_message",
                           LoopingCall(self.send_message_console)).start(50 , now=True)



    def initiate_meta_messages(self):
        '''
        Create the packaging for your message payloads,
        in this case we have one message type that is distributed to all peers
        '''

        return super(ExampleCommunity, self).initiate_meta_messages() + [
            Message(self, u"message",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    LastSyncDistribution(synchronization_direction=u"DESC", priority=128, history_size=10),
                    CommunityDestination(node_count=10),
                    MessagePayload(),
                    self.check_message,
                    self.on_message,
                    batch=BatchConfiguration(max_window=3.0)),
            Message(self, u"message-user",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    DirectDistribution(),
                    CommunityDestination(node_count=10),
                    MessagePayload(),
                    self.check_message,
                    self.on_message_user,
                    batch=BatchConfiguration(max_window=3.0)),

        ]

    def send_message_console(self):
        msg = raw_input("You: ")
        self.send_message(msg)

    def initiate_conversions(self):
        return [DefaultConversion(self), Conversion(self)]

    def check_message(self, messages):
        "Authentication of our Meta Message happens here, in this case every message is authorized"

        for message in messages:
            yield message

    def on_message(self, messages):
        "Called after check_text, we can now display our message to the user"

        for message in messages:
            if message.authentication.member.mid == self.my_member.mid:
                # if we sent the message, ignore
                continue
            print 'Stranger: ', message.payload.text

    def send_message(self, text='testing'):
        meta = self.get_meta_message(u"message")
        message = meta.impl(authentication=(self.my_member,),
                          distribution=(self.claim_global_time(),),
                          payload=(unicode(text),))
        self.dispersy.store_update_forward([message], True, True, True)

    def on_message_user(self, messages):
        "Called after check_text, we can now display our message to the user"

        for message in messages:
            if message.authentication.member.mid == self.my_member.mid:
                # if we sent the message, ignore
                continue
            print 'Stranger: ', message.payload.text

    def send_message_user(self, message, candidate):
        meta = self.get_meta_message(u"message-user")
        message = meta.impl(authentication=(self.my_member,),
                          distribution=(self.claim_global_time(),),
                          payload=(unicode(message),))
        self.dispersy._send([candidate], [message])


