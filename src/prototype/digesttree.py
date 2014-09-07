import hashlib

class DigestTree:

    def __init__(self, our_name):
        # Dictionary of producer names and their sequences
        self.children = {}
        self.last_digest = None
        #self.add_branch(our_name)

    def calculate_root(self):
        keys = list(self.children)
        keys.sort()
        sha1 = hashlib.sha1()
        if len(keys) > 1:
            for key in keys:
                sha1.update(key + str(self.children[key]))
        self.last_digest = sha1.hexdigest()
        return self.last_digest

    def add_branch(self, prod_name, seq=0):
        try:
            self.children[prod_name]
        except KeyError:
            self.children[prod_name] = seq
        self.calculate_root()

    def update_seq(self, prod_name, seq):
        old_val = self.children[prod_name]
        if old >= seq:
            raise OutOfOrderSequence
        else:
            self.children[prod_name] = seq
            self.calculate_root()
    
    def get_root(self):
        return self.last_digest


class OutOfOrderSequence(Exception):
    # Raised when we try to update a sequence with an smaller number
    def __init__(self):
        pass


class DigestLog:
    # Keeps a copy of old digest and the status that have changed since.
    def __init__(self):
        pass

