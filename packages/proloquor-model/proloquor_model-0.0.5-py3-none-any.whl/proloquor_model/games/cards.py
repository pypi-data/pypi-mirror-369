from enum import Enum
import numpy as np

class Suit(Enum):
    CLUBS    = 1
    DIAMONDS = 2
    HEARTS   = 3
    SPADES   = 4

class Rank(Enum):
    TWO   = 2
    THREE = 3
    FOUR  = 4
    FIVE  = 5
    SIX   = 6
    SEVEN = 7
    EIGHT = 8
    NINE  = 9
    TEN   = 10
    JACK  = 11
    QUEEN = 12
    KING  = 13
    ACE   = 14

class Card:
    def __init__(self, rank = Rank.ACE, suit = Suit.SPADES):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        suits = [None, "\u2663", "\u2666", "\u2665", "\u2660"]
        ranks = [None, None, "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        return f"{ranks[self.rank.value]}{suits[self.suit.value]}"
    
class Deck:
    def __init__(self):
        self.cards = []
        self.ranks = {r: 0 for r in Rank}
        self.suits = {s: 0 for s in Suit}

    def __str__(self):
        return ", ".join([str(c) for c in self.cards])
    
    def __len__(self):
        return len(self.cards)
    
    def add(self, card: Card):
        self.cards.append(card)
        self.ranks[card.rank] += 1
        self.suits[card.suit] += 1
        return self
    
    def draw(self, replace = False):
        if len(self) == 0:
            raise Exception("Deck is empty.")
        
        if replace:
            return self.cards[-1]
        
        card = self.cards.pop()
        self.ranks[card.rank] -= 1
        self.suits[card.suit] -= 1
        return card
    
    def shuffle(self):
        np.random.shuffle(self.cards)
        return self
    
    def howMany(self, rank = None, suit = None):
        if rank is not None and suit is not None:
            return len([c for c in self.cards if c.rank == rank and c.suit == suit])
        
        if rank is not None:
            return self.ranks[rank]
        
        if suit is not None:
            return self.suits[suit]
        
        return len(self)

class PokerDeck(Deck):
    def __init__(self):
        super().__init__()
        for rank in Rank:
            for suit in Suit:
                self.add(Card(rank, suit))