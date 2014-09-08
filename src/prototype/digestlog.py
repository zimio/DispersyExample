


class DigestLog():

    def __init__(self):
        # Log of the last 50 messages sent by everyone
        self.msg_limit = 50
        self.log = {}

    def add(self, mid, seq, msg):
        if mid in self.log.keys():
            member_msgs = self.log[mid]
            if len(member_msgs) >= 50:
                # keys() returns a sorted list
                oldest = member_msgs.keys()[0] 
                member_msgs.pop(oldest)
            member_msgs[seq] = msg
        else:
            self.log[mid] = {seq : msg}

    def remove(self, mid):
        self.log.pop(mid)

    def get_msg(self, mid, seq):
        return self.log[mid][seq]


