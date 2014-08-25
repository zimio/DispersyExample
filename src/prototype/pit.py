


# Pending Interest Table
class PIT():

    def __init__(self):
        self.table = []
        # if we are 15 messages behind global time, prune old messages
        self.time_limit = 15 

    def get_sync(self, digest):
        # Return items in the table with the same digest
        syncs = []
        for message in self.table:
            if message.meta.name == u'sync' and message.payload.digest == digest:
                syncs.append(message)
        return syncs

    def get_interest(self, producer, seq):
        # Return items in the table with the same sequence number
        interests = []
        for message in self.table:
            if message.meta.name == 'interest' and message.payload.producer == producer \
                    and message.payload.seq_number == seq:
                interests.append(message)
        return interests

    def prune_old(self, global_time):
        # Delete old items after a certain time has pass
        old = []
        for message in self.table:
            if (message.distribution.global_time + self.time_limit) <= global_time:
                old.append(message)
        self.remove(old)

    def add(self, message):
        self.table.append(message)

    def remove(self, items):
        for item in items:
            self.table.remove(item)

