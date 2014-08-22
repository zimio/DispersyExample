import hashlib

class DigestTree:

    def __init__(self):
        # Dictionary of producer names and their sequences
        self.children = {}
        self.last_digest = None

    def calculate_root(self):
        keys = list(self.children)
        keys.sort()
        sha256 = hashlib.sha256()
        for key in keys:
            sha256.update(key + str(self.children[key]))
        self.last_digest = sha256.digest()
        return self.last_digest

    def add_branch(self, prod_name, seq=0):
        try:
            self.children[prod_name]
        except KeyError:
            self.children[prod_name] = seq

    def update_seq(self, prod_name, seq):
        old_val = self.children[prod_name]
        if old => seq:
            raise OutOfOrderSequence
        else:
            self.children[prod_name] = seq


class OutOfOrderSequence(Exception):
    
    def __init__(self):
        pass

