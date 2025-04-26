import random
from constants import *

class Deck:
    def __init__(self):
        self.cards = []
        self.discarded = []
        self.num_decks = 2
        self.build()
        self.shuffle()

    def build(self):
        #Створює нову колоду з 52 карт
        self.cards = []
        for i in range(self.num_decks):
            self.cards.extend([(suit, value) for suit in SUITS for value in RANKS])
        self.initial_count = len(self.cards)

    def shuffle(self):
        #Перемішує колоду
        random.shuffle(self.cards)

    def deal(self):
        #Роздає одну карту з колоди, автоматично перемішує при необхідності
        if len(self.cards) == 0:
            # Якщо карти закінчились, перемішуємо відкинуті карти
            self.cards = self.discarded.copy()
            self.discarded = []
            self.shuffle()
        
        if len(self.cards) == 0:
            # Якщо все ще немає карт (не було відкинутих)
            self.build()
            self.shuffle()
        
        card = self.cards.pop()
        self.discarded.append(card)
        return card

    def remaining_cards(self):
        #Повертає кількість карт, що залишились у колоді
        return len(self.cards)

    def reset(self):
        #Повністю скидає колоду (новий початок гри)
        self.build()
        self.shuffle()

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
    def clear(self):
        #Очищає руку
        self.cards = []
        self.card_img = []
        self.value = 0