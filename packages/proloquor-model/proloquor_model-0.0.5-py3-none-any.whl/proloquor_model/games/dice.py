from enum import Enum
import numpy as np

class DieSide(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6

class Die:
    def __init__(self):
        self.side = DieSide.ONE

    def __str__(self):
        return str(self.side.value)
    
    def roll(self):
        self.side = np.random.choice(DieSide)
        return self
    
class Dice:
    def __init__(self, num=5):
        self.dice = [Die() for i in range(num)]

    def __str__(self):
        return ", ".join([str(d) for d in self.dice])
    
    def __len__(self):
        return len(self.dice)
    
    def roll(self):
        for d in self.dice:
            d.roll()
        return self
    
    def total(self):
        return np.sum([d.side.value for d in self.dice])