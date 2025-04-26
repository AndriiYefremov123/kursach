import unittest
from blackjack_deck import *

class TestDeck(unittest.TestCase):
    def test_deck_initialization(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 104, "Deck should start with 52 cards.")

    def test_deal_card(self):
        deck = Deck()
        card = deck.deal()
        self.assertIsNotNone(card, "Dealt card should not be None.")
        self.assertEqual(len(deck.cards), 103, "Deck should have 51 cards after dealing one.")

    def test_shuffle_changes_order(self):
        deck1 = Deck()
        deck2 = Deck()
        deck2.shuffle()
        self.assertNotEqual(deck1.cards, deck2.cards, "Shuffled deck should be different from original.")

class TestHand(unittest.TestCase):
    def test_hand_add_card(self):
        hand = Hand()
        hand.add_card(('H', 'A'))
        self.assertEqual(len(hand.cards), 1, "Hand should have one card after adding.")

    def test_hand_value_calculation(self):
        hand = Hand()
        hand.add_card(('H', 'A')) # Припустимо, у тебе є обробка для 'A'
        hand.add_card(('H', '10'))
        hand.calc_hand()
        self.assertTrue(hand.value in [11, 21], "Hand value should be calculated correctly.")
    def test_hand_two_aces(self):
        hand = Hand()
        hand.add_card(('H', 'A'))
        hand.add_card(('C', 'A'))
        hand.calc_hand()
        self.assertEqual(hand.value, 12, "Hand with two aces should be 12 (11 + 1)")
    def test_hand_aces_adjustment(self):
        hand = Hand()
        hand.add_card(('C', 'A'))
        hand.add_card(('H', '9'))
        hand.add_card(('D', '5'))
        hand.calc_hand()
        self.assertEqual(hand.value, 15, "Ace should adjust to 1 if necessary to avoid bust")



if __name__ == '__main__':
    unittest.main()
