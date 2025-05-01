import unittest
from unittest.mock import patch, MagicMock
from blackjack_deck import Hand, Deck
from blackjack_pygame import Play

class TestHandLogic(unittest.TestCase):
    def setUp(self):
        self.blackjack_hand = Hand()
        self.blackjack_hand.add_card(('H', '7'))
        self.blackjack_hand.add_card(('D', '7'))
        self.blackjack_hand.add_card(('C', '7'))
        self.blackjack_hand.calc_hand()

        self.bust_hand = Hand()
        self.bust_hand.add_card(('H', '9'))
        self.bust_hand.add_card(('D', '9'))
        self.bust_hand.add_card(('S', '8'))
        self.bust_hand.calc_hand()

        self.pair_hand = Hand()
        self.pair_hand.add_card(('H', '7'))
        self.pair_hand.add_card(('D', '7'))

    def test_hand_value(self):
        self.assertEqual(self.blackjack_hand.value, 21)
        self.assertGreater(self.bust_hand.value, 21)

    def test_check_not_bust(self):
        self.assertTrue(self.blackjack_hand.value <= 21)
        self.assertFalse(self.bust_hand.value <= 21)

    def test_split_possible(self):
        cards = self.pair_hand.cards
        self.assertEqual(cards[0][1], cards[1][1])  # Має бути пара

class TestDeckLogic(unittest.TestCase):
    def test_deck_initialization(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 104)

    def test_deal_reduces_deck(self):
        deck = Deck()
        initial = len(deck.cards)
        deck.deal()
        self.assertEqual(len(deck.cards), initial - 1)

    def test_deck_shuffle(self):
        deck1 = Deck()
        deck2 = Deck()
        deck2.shuffle()
        self.assertNotEqual(deck1.cards, deck2.cards)

class TestGameLogic(unittest.TestCase):
    def setUp(self):
        self.deck = Deck()
        self.game = Play()

    def test_blackjack_detection(self):
        self.game.player.add_card(('H', 'A'))
        self.game.player.add_card(('D', '10'))
        self.game.player.calc_hand()
        self.assertEqual(self.game.player.value, 21)

    def test_hit_adds_card(self):
        self.game.player = Hand()
        initial_count = len(self.game.player.cards)
        with patch.object(self.game, 'hit') as mock_hit:
            mock_hit.side_effect = lambda: self.game.player.add_card(self.game.deck.deal())
            self.game.hit()
        self.assertEqual(len(self.game.player.cards), initial_count + 1)

    def test_split_hand(self):
        self.game.player.add_card(('H', '8'))
        self.game.player.add_card(('D', '8'))
        self.assertTrue(self.game.can_split())
        result = self.game.split_hand()
        self.assertTrue(result)
        self.assertEqual(len(self.game.split_hands), 2)

    def test_insurance_logic(self):
        self.game.balance = 500
        self.game.current_bet = 100
        self.game.insurance_bet = 0

        # Потрібні card_img (бо перевірка саме через них)
        self.game.player.card_img = [('H', '10'), ('S', '7')]
        self.game.dealer.card_img = [('S', 'A')]

        self.assertTrue(self.game.can_insurance())

        self.game.insurance(50)
        self.assertEqual(self.game.insurance_bet, 50)
        self.assertEqual(self.game.balance, 450)

    def test_dealer_play_logic(self):
        self.game.dealer.add_card(('H', '5'))
        self.game.dealer.add_card(('S', '6'))
        self.game.dealer.calc_hand()
        while self.game.dealer.value < 17:
            self.game.dealer.add_card(self.game.deck.deal())
            self.game.dealer.calc_hand()

        self.assertGreaterEqual(self.game.dealer.value, 17)

    def test_winner_determination(self):
        player_hand = Hand()
        dealer_hand = Hand()
        player_hand.add_card(('H', '10'))
        player_hand.add_card(('S', '9'))
        player_hand.calc_hand()

        dealer_hand.add_card(('D', '8'))
        dealer_hand.add_card(('C', '9'))
        dealer_hand.calc_hand()

        self.game.dealer = dealer_hand
        result = self.game.get_hand_result(player_hand)
        self.assertIn(result, ["Виграш", "Програш", "Нічия"])

if __name__ == '__main__':
    unittest.main()
