from enum import Enum
import numpy as np

class CoinSide(Enum):
    HEADS = 1
    TAILS = 2

class Coin:
    def __init__(self):
        self.side = CoinSide.HEADS

    def __str__(self):   
        symbols = [None, 'H', 'T'] 
        return symbols[self.side.value]
    
    def flip(self):
        self.side = np.random.choice([c for c in CoinSide])
        return self
    