import logging

from .conversion import Conversion
from .payload import SyncPayload, DataPayload, InterestPayload
from .digesttree import DigestTree
from .pit import PIT

from dispersy.authentication import MemberAuthentication
from dispersy.community import Community
from dispersy.conversion import DefaultConversion
from dispersy.destination import CommunityDestination
from dispersy.distribution import FullSyncDistribution
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
        #self.send_data(msg)
        self.register_task("send_data",
                           LoopingCall(self.send_data_console)).start(50 , now=True)



    def initiate_meta_messages(self):
        '''
        Create the packaging for your message payloads,
        in this case we have one message type that is distributed to all peers
        '''

        return super(ExampleCommunity, self).initiate_meta_messages() + [
            Message(self, u"sync",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    FullSyncDistribution(enable_sequence_number=False, synchronization_direction=u"ASC", priority=128),
                    CommunityDestination(node_count=10),
                    SyncPayload(),
                    self.check_sync,
                    self.on_sync,
                    batch=BatchConfiguration(max_window=3.0)),
            Message(self, u"interest",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    FullSyncDistribution(enable_sequence_number=False, synchronization_direction=u"ASC", priority=128),
                    CommunityDestination(node_count=10),
                    InterestPayload(),
                    self.check_interest,
                    self.on_interest,
                    batch=BatchConfiguration(max_window=3.0)),
            Message(self, u"data",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    FullSyncDistribution(enable_sequence_number=False, synchronization_direction=u"ASC", priority=128),
                    CommunityDestination(node_count=10),
                    DataPayload(),
                    self.check_data,
                    self.on_data,
                    batch=BatchConfiguration(max_window=3.0)),

        ]

    def send_data_console(self):
        msg = raw_input("You: ")
        self.send_data(msg)

    def initiate_conversions(self):
        return [DefaultConversion(self), Conversion(self)]

    def check_sync(self, messages):
        "Authentication of our Meta Message happens here, in this case every message is authorized"

        for message in messages:
            yield message

    def on_sync(self, messages):
        for message in messages:
            self.pit.add(message)
            # if it is the empty digest, send our empty digest
            # NOTE: if not DirectDistribution, only send once
            # if digest is equal, do nothing
            # if digest is not equal, try to find it in the log
            # if it is in digest log, send the statuses that changed since
            # if it isn't, send known statuses and then send our sync


    def check_interest(self, messages):
        "Authentication of our Meta Message happens here, in this case every message is authorized"

        for message in messages:
            yield message

    def on_interest(self, messages):
        "Called after check_text, we can now display our message to the user"

        for message in messages:
            print 'someone says', message.payload.text
            logging.info("someone says '%s'", message.payload.text)

    def check_data(self, messages):
        "Authentication of our Meta Message happens here, in this case every message is authorized"

        for message in messages:
            yield message

    def on_data(self, messages):
        "Called after check_text, we can now display our message to the user"

        for message in messages:
            if message.authentication.member.mid == self.my_member.mid:
                # if we sent the message, ignore
                continue
            print 'Stranger: ', message.payload.text

    def send_data(self, text='testing'):
        meta = self.get_meta_message(u"data")
        message = meta.impl(authentication=(self.my_member,),
                          distribution=(self.claim_global_time(),),
                          payload=(unicode(text),))
        self.dispersy.store_update_forward([message], True, True, True)


