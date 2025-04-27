
from blackjack_deck import *
from blackjack_pygame import Play
import unittest

#Юніт тести для різних ситуацій у грі
class TestDeck(unittest.TestCase):
    def test_deck_initialization(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 104, "Deck should start with 104 cards.")

    def test_deal_card(self):
        deck = Deck()
        card = deck.deal()
        self.assertIsNotNone(card, "Dealt card should not be None.")
        self.assertEqual(len(deck.cards), 103, "Deck should have 103 cards after dealing one.")

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
        hand.add_card(('H', 'A')) # 
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

class TestPlayInsurance(unittest.TestCase):
    def setUp(self):
        self.game = Play()
        # Імітуємо початковий стан гри
        self.game.dealer = Hand()
        self.game.player = Hand()
        self.game.balance = 1000
        self.game.current_bet = 400  # Поточна ставка гравця
        
        # Додаємо карти дилеру (туз і 10)
        self.game.dealer.add_card(('S', 'A'))
        self.game.dealer.add_card(('H', '10'))
        
        # Додаємо карти гравцю (будь-які дві карти)
        self.game.player.add_card(('D', '8'))
        self.game.player.add_card(('C', '9'))
        
        # Оновлюємо значення рук
        self.game.dealer.calc_hand()
        self.game.player.calc_hand()

    def test_can_insurance_conditions(self):
        """Тест умов для доступності страхування"""
        # Стандартний випадок - має бути доступно
        self.assertTrue(self.game.can_insurance())
        
        # Коли у дилера немає туза
        self.game.dealer = Hand()
        self.game.dealer.add_card(('S', 'K'))
        self.game.dealer.add_card(('H', '10'))
        self.assertFalse(self.game.can_insurance())
        
        # Коли у гравця не дві карти
        self.game.player = Hand()
        self.game.player.add_card(('D', '8'))
        self.assertFalse(self.game.can_insurance())
        
        # Коли вже зроблено страховку
        self.game.insurance_bet = 100
        self.assertFalse(self.game.can_insurance())

    def test_insurance_bet_placement(self):
        """Тест розміщення страхової ставки"""
        # Максимальна допустима страховка (1/2 поточної ставки)
        max_insurance = min(self.game.current_bet // 2, self.game.balance)
        
        # Спроба зробити страховку
        self.assertTrue(self.game.can_insurance())
        self.game.insurance(max_insurance)
        
        # Перевірка результатів
        self.assertEqual(self.game.insurance_bet, max_insurance)
        self.assertEqual(self.game.balance, 1000 - max_insurance)
        
        # Спроба зробити ще одну страховку (має бути неможливо)
        with self.assertRaises(Exception):
            self.game.insurance(100)

    def test_insurance_payout(self):
        """Тест виплат за страховку"""
        # Випадок, коли дилер має блекджек
        self.game.insurance(200)
        self.game.dealer.value = 21  # Блекджек дилера
        self.game.check_insurance()
        
        # Перевірка виплати 2:1
        self.assertEqual(self.game.balance, 1000 - 200 + 400)  # -200 + 400
        self.assertEqual(self.game.insurance_bet, 0)
        
        # Випадок, коли дилер не має блекджеку
        self.game.insurance(200)
        self.game.dealer.value = 20  # Немає блекджеку
        self.game.check_insurance()
        
        # Страховка має бути втрачена
        self.assertEqual(self.game.balance, 1000 - 200 + 400 - 200)
        self.assertEqual(self.game.insurance_bet, 0)

    def test_insurance_edge_cases(self):
        """Тест крайніх випадків"""
        # Спроба зробити страховку більше ніж 1/2 ставки
        with self.assertRaises(ValueError):
            self.game.insurance(self.game.current_bet // 2 + 1)
            
        # Спроба зробити страховку при нульовому балансі
        self.game.balance = 0
        self.game.insurance_bet = 0  # Скидаємо попередню страховку
        self.assertFalse(self.game.can_insurance(), 
                       "При нульовому балансі страхування має бути недоступне")
        
        # Додаткова перевірка - якщо немає туза у дилера
        self.game.dealer = Hand()
        self.game.dealer.add_card(('S', 'K'))  # Додаємо карти без туза
        self.game.dealer.add_card(('H', '10'))
        self.assertFalse(self.game.can_insurance(),
                       "Без туза у дилера страхування має бути недоступне")





if __name__ == '__main__':
    unittest.main()
