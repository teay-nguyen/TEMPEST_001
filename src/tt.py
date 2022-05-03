
from sys import getsizeof
from dataclasses import dataclass

HASH_EXACT:int = 0; HASH_ALPHA:int = 1; HASH_BETA:int = 2
NO_HASH_ENTRY:int = 100000

@dataclass
class tt_entry:
    hash_key:int = 0
    depth:int = 0
    flag:int = 0
    score:int = 0

class Transposition:
    def __init__(self):
        self.hash_table:list = []
        self.hash_entries:int = 0

    def init_hashtable(self, mb:int):
        # define hash size
        hash_size:int = 0x100000 * mb

        # determine the number of hash entries
        self.hash_entries = hash_size // getsizeof(tt_entry)

        # clear hash table if not empty
        if len(self.hash_table) != 0:
            self.hash_table = []

        # renew hash table
        self.hash_table = [tt_entry() for _ in range(self.hash_entries * getsizeof(tt_entry))]

    def clear_hashtable(self):
        # loop through hash table and reset every entry
        for idx in range(len(self.hash_table)):
            self.hash_table[idx].hash_key = 0
            self.hash_table[idx].depth = 0
            self.hash_table[idx].flag = 0
            self.hash_table[idx].score = 0

    def tt_probe(self, alpha, beta, depth, hash_key) -> int:
        # the formula to indexing is the zobrist key % size of hash table
        hash_entry = self.hash_table[hash_key % self.hash_entries]

        # check if we're dealing with the exact position needed
        if hash_entry.hash_key == hash_key:
            # ensure the depth being searched at is matched
            if hash_entry.depth >= depth:
                # this part is eelf explanitory
                score:int = hash_entry.score
                if hash_entry.flag == HASH_EXACT: return score
                if hash_entry.flag == HASH_ALPHA and score <= alpha: return alpha
                if hash_entry.flag == HASH_BETA and score >= beta: return beta
        # return an impossible value if no hash entry is found or no criteria above is met
        return NO_HASH_ENTRY

    def tt_write(self, score, depth, hash_flag, hash_key):
        hash_entry = self.hash_table[hash_key % self.hash_entries]

        if hash_entry.hash_key == hash_key and hash_entry.depth > depth: return

        hash_entry.hash_key = hash_key
        hash_entry.depth = depth
        hash_entry.flag = hash_flag
        hash_entry.score = score
