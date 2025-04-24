import random
from constants import *

class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        self.cards = [(suit, value) for suit in SUITS for value in RANKS]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        if len(self.cards) < 1:
            self.build()
            self.shuffle()
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
        self.card_img = []
        self.value = 0

    def add_card(self, card):
        self.cards.append(card)
        self.card_img.append(f"{card[0]}{card[1]}")  # одразу додаємо зображення карти

    def calc_hand(self):
        self.value = 0
        aces = 0

        for card in self.cards:
            rank = card[1]
            if rank == 'A':
                aces += 1
                self.value += 11
            elif rank in ['J', 'Q', 'K']:
                self.value += 10
            else:
                self.value += int(rank)

        while self.value > 21 and aces:
            self.value -= 10
            aces -= 1
