import logging

from .conversion import Conversion, StatusConversion, EmptyConversion, SearchConversion
from .payload import MessagePayload, StatusPayload, EmptyPayload, NickPayload, SearchPayload
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
            Message(self, u"status",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    LastSyncDistribution(synchronization_direction=u"DESC", priority=128, history_size=10),
                    CommunityDestination(node_count=10),
                    StatusPayload(),
                    self.check_status,
                    self.on_status,
                    batch=BatchConfiguration(max_window=3.0)),
            Message(self, u"set-status",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    DirectDistribution(),
                    CommunityDestination(node_count=10),
                    StatusPayload(),
                    self.check_status,
                    self.on_status,
                    batch=BatchConfiguration(max_window=3.0)),
            Message(self, u"get-status",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    DirectDistribution(),
                    CommunityDestination(node_count=10),
                    EmptyPayload(),
                    self.check_empty,
                    self.on_get_status,
                    batch=BatchConfiguration(max_window=3.0)),
            Message(self, u"nick",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    LastSyncDistribution(synchronization_direction=u"DESC", priority=128, history_size=10),
                    CommunityDestination(node_count=10),
                    NickPayload(),
                    self.check_nick,
                    self.on_nick,
                    batch=BatchConfiguration(max_window=3.0)),
            Message(self, u"set-nick",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    DirectDistribution(),
                    CommunityDestination(node_count=10),
                    NickPayload(),
                    self.check_nick,
                    self.on_nick,
                    batch=BatchConfiguration(max_window=3.0)),
            Message(self, u"get-nick",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    DirectDistribution(),
                    CommunityDestination(node_count=10),
                    EmptyPayload(),
                    self.check_empty,
                    self.on_get_nick,
                    batch=BatchConfiguration(max_window=3.0)),
            Message(self, u"keepalive",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    LastSyncDistribution(synchronization_direction=u"DESC", priority=128, history_size=10),
                    CommunityDestination(node_count=10),
                    EmptyPayload(),
                    self.check_empty,
                    self.on_keepalive,
                    batch=BatchConfiguration(max_window=3.0)),
            Message(self, u"search",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    LastSyncDistribution(synchronization_direction=u"DESC", priority=128, history_size=10),
                    CommunityDestination(node_count=10),
                    SearchPayload(),
                    self.check_search,
                    self.on_search,
                    batch=BatchConfiguration(max_window=3.0)),
            Message(self, u"search-user",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    DirectDistribution(),
                    CommunityDestination(node_count=10),
                    SearchPayload(),
                    self.check_search,
                    self.on_search,
                    batch=BatchConfiguration(max_window=3.0)),



        ]

    def send_message_console(self):
        msg = raw_input("You: ")
        self.send_message(msg)

    def initiate_conversions(self):
        return [DefaultConversion(self), Conversion(self), StatusConversion(self), 
                EmptyConversion(self), SearchConversion(self)]

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

    def check_status(self, messages):
        "Authentication of our Meta Message happens here, in this case every message is authorized"

        for message in messages:
            yield message

    def on_status(self, messages):
        "Called after check_text, we can now display our message to the user"

        for message in messages:
            if message.authentication.member.mid == self.my_member.mid:
                # if we sent the message, ignore
                continue
            print 'Status: ', message.payload.status

    def send_status(self, status):
        meta = self.get_meta_message(u"status")
        message = meta.impl(authentication=(self.my_member,),
                          distribution=(self.claim_global_time(),),
                          payload=(status,))
        self.dispersy.store_update_forward([message], True, True, True)

    def check_empty(self, messages):
        # Checks empty payloads

        for message in messages:
            yield message

    def on_get_status(self, messages):
        "Called after check_text, we can now display our message to the user"

        for message in messages:
            if message.authentication.member.mid == self.my_member.mid:
                # if we sent the message, ignore
                continue
            print 'get status recieved'

    def send_get_status(self, candidate):
        meta = self.get_meta_message(u"get-status")
        message = meta.impl(authentication=(self.my_member,),
                          distribution=(self.claim_global_time(),),
                          payload=('0',))
        self.dispersy._send([candidate], [message])

    def check_nick(self, messages):
        # nicks have a limit of 12 characters
        # nicks are not allowed to have weird special characters
        # maybe make then utf-8

        for message in messages:
            yield message

    def on_nick(self, messages):
        "Called after check_text, we can now display our message to the user"

        for message in messages:
            if message.authentication.member.mid == self.my_member.mid:
                # if we sent the message, ignore
                continue
            print 'nick recieved: ' + message.payload.nick

    def send_nick(self, nick):
        meta = self.get_meta_message(u"nick")
        message = meta.impl(authentication=(self.my_member,),
                          distribution=(self.claim_global_time(),),
                          payload=(unicode(nick),))
        self.dispersy.store_update_forward([message], True, True, True)

    def on_keepalive(self, messages):

        for message in messages:
            if message.authentication.member.mid == self.my_member.mid:
                # if we sent the message, ignore
                continue
            print 'nick recieved: ' + message.payload.nick

    def check_search(self, messages):

        for message in messages:
            yield message

    def on_get_nick(self, messages):
        for message in messages:
            if message.authentication.member.mid == self.my_member.mid:
                # if we sent the message, ignore
                continue
            print 'get nick recieved: '


    def on_search(self, messages):
        "Called after check_text, we can now display our message to the user"

        for message in messages:
            if message.authentication.member.mid == self.my_member.mid:
                # if we sent the message, ignore
                continue
            print 'search recieved: ' + message.payload.keywords
            print 'search recieved: ' + message.payload.file_type

    def send_search(self, keywords, file_type):
        meta = self.get_meta_message(u"search")
        message = meta.impl(authentication=(self.my_member,),
                          distribution=(self.claim_global_time(),),
                          payload=(unicode(keywords), unicode(file_type)))
        self.dispersy.store_update_forward([message], True, True, True)

