
# imports
from sys import getsizeof
from dataclasses import dataclass

# variables
HASH_EXACT:int = 0; HASH_ALPHA:int = 1; HASH_BETA:int = 2; NO_HASH_ENTRY:int = 100000

# entries
@dataclass
class tt_entry:
    hash_key:int = 0
    depth:int = 0
    flag:int = 0
    score:int = 0

@dataclass
class tteval_entry:
    hash_key:int = 0
    score:int = 0

# main driver
class Transposition:
    def __init__(self):
        self.tt_table:list = list()
        self.tteval_table:list = list()

        self.tt_size:int = 0
        self.tteval_size:int = 0
    
    def tt_setsize(self, size:int):
        self.tt_size = size

    def tt_probe(self, depth, alpha, beta, hashkey):
        # checks the table for any record of the position before actually parsing and calculating the position
        # this is the whole purpose of the transposition table

        if not self.tt_size: return NO_HASH_ENTRY

        # get entry from table
        entry = self.tt_table[hashkey % self.tt_size]

        # return score based on flag
        if entry.hash_key == hashkey:
            if entry.depth >= depth:
                if entry.flag == HASH_EXACT: return entry.score
                elif entry.flag == HASH_ALPHA and entry.score <= alpha: return alpha
                elif entry.flag == HASH_BETA and entry.score >= beta: return beta

        # there is no valid entry, return no hash value
        return NO_HASH_ENTRY

    def tt_save(self, depth, score, flag, hashkey):
        if not self.tt_size: return

        # get entry from table
        entry = self.tt_table[hashkey % self.tt_size]

        # if there is a better entry scrap this one
        if entry.hash_key == hashkey and entry.depth > depth: return

        # set the value
        entry.hash_key = hashkey
        entry.score = score
        entry.flag = flag
        entry.depth = depth

    def tteval_setsize(self, size:int):
        self.tteval_size = size
    
    def tteval_probe(self, hashkey):
        if not self.tteval_size: return NO_HASH_ENTRY
        entry = self.tteval_table[hashkey % self.tteval_size]
        if entry.hash_key == hashkey: return entry.score
        return NO_HASH_ENTRY

    def tteval_save(self, score, hashkey):
        if not self.tteval_size: return
        entry = self.tteval_table[hashkey % self.tteval_size]
        entry.hash_key = hashkey
        entry.score = score
