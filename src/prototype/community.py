import logging
import datetime
import pickle
import sys

from .conversion import Conversion
from .payload import SyncPayload, DataPayload, InterestPayload
from .digesttree import DigestTree
from .pit import PIT

from dispersy.authentication import MemberAuthentication
from dispersy.community import Community
from dispersy.conversion import DefaultConversion
from dispersy.destination import CommunityDestination
from dispersy.distribution import FullSyncDistribution, LastSyncDistribution
from dispersy.message import BatchConfiguration, Message, DelayMessageByProof
from dispersy.resolution import PublicResolution

from twisted.internet.task import LoopingCall


class ExampleCommunity(Community):

    # @property
    # def dispersy_auto_download_master_member(self):
    #     # there is no dispersy-identity for the master member, so don't try to download (???)
    #     return False

    def initialize(self, file_name):
        "Called After init_community is called"

        super(ExampleCommunity, self).initialize()
        logging.info("ExampleCommunity Initalized")
        #self.send_data(msg)
        self.msg_number = 0
        # Dictionary with the sequence of every message sent
        self.messages_recv = {}
        # Limit of messages sent and recieved
        self.limit_msgs = 100
        # Total delay of messages
        self.delay = None

        self.file_name = file_name
        



        self.start_task= self.register_task("check_time",
                           LoopingCall(self.check_time))
        self.start_task.start(1 , now=True)
        self.task = self.register_task("send_data",
                           LoopingCall(self.send_data_console))
        self.finish_task = self.register_task("finish",
                           LoopingCall(self.save_finish))
        self.number_msg_recv = 0
 



    def initiate_meta_messages(self):
        '''
        Create the packaging for your message payloads,
        in this case we have one message type that is distributed to all peers
        '''
        return super(ExampleCommunity, self).initiate_meta_messages() + [
            Message(self, u"data",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    LastSyncDistribution(synchronization_direction=u"DESC", priority=128, history_size=10),
                    CommunityDestination(node_count=1),
                    DataPayload(),
                    self.check_data,
                    self.on_data,
                    batch=BatchConfiguration(max_window=1.0)),

        ]

    def save_finish(self):
        # saves the information in a file and finishes
        output = open('../data/' + self.file_name, 'wb')
        avgdelay = self.delay / self.number_msg_recv
        missed_messages = 0
        for msg_lst in self.messages_recv.values():
            missed_messages = missed_messages + (self.limit_msgs - len(msg_lst))
        pickle.dump((avgdelay, missed_messages), output)
        output.close()
        print 'file close'
        self.finish_task.stop()

    def check_time(self):
        # starts task on a determined time
        tminute = 33
        if tminute == datetime.datetime.now().minute:
            self.task.start(6 , now=True)
            self.start_task.stop()



    def send_data_console(self):
        if self.msg_number >= self.limit_msgs:
            self.task.stop()
            self.finish_task.start(100 , now=False)
            print 'end of task'
            return
        self.msg_number = self.msg_number + 1
        msg = str(datetime.datetime.now()) + ';' + str(self.msg_number)
        print 'sending message: ' + str(self.msg_number)
        self.send_data(msg)

    def initiate_conversions(self):
        return [DefaultConversion(self), Conversion(self)]


    def check_data(self, messages):
        "Authentication of our Meta Message happens here, in this case every message is authorized"

        for message in messages:
            time, number = message.payload.text.split(';')
            mid = message.authentication.member.mid
            if mid in self.messages_recv.keys() and number in self.messages_recv[mid]:
                print 'found duplicate'
                continue
            yield message

    def add_delay(self, ftime):
        if self.delay == None:
            self.delay = datetime.datetime.now() - ftime
        else:
            self.delay = self.delay + datetime.datetime.now() - ftime

    def add_number(self, number, mid):
        if not (mid in self.messages_recv.keys()):
            self.messages_recv[mid] = []
        self.messages_recv[mid].append(number)

    def on_data(self, messages):
        "Called after check_text, we can now display our message to the user"
        dateformat = '%Y-%m-%d %H:%M:%S.%f'

        for message in messages:
            if message.authentication.member.mid == self.my_member.mid:
                # if we sent the message, ignore
                continue
            time, number = message.payload.text.split(';')
            ftime = datetime.datetime.strptime(time, dateformat)
            self.add_delay(ftime)
            self.add_number(int(number), message.authentication.member.mid)
            self.number_msg_recv = self.number_msg_recv + 1
            print 'recieved: ' + number + ' delay:' + str((datetime.datetime.now() - ftime).total_seconds())

    def send_data(self, text='testing'):
        meta = self.get_meta_message(u"data")
        message = meta.impl(authentication=(self.my_member,),
                          distribution=(self.claim_global_time(),),
                          payload=(unicode(text),))
        self.dispersy.store_update_forward([message], True, True, True)


