import random

def create_deck():
    """Створює стандартну колоду з 52 карт."""
    suits = ['♠', '♥', '♦', '♣']
    values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
    deck = [(f"{rank}{suit}", values[rank]) for suit in suits for rank in values]
    random.shuffle(deck)
    return deck

def calculate_total(cards):
    """Обчислює суму карт з урахуванням туза."""
    total = sum(card[1] for card in cards)
    aces = sum(1 for card in cards if 'A' in card[0])
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def play_blackjack():
    """Головна функція гри в блекджек."""
    while True:
        deck = create_deck()
        
        player_cards = [deck.pop(), deck.pop()]
        dealer_cards = [deck.pop(), deck.pop()]
        
        print(f"Ваша перша карта: {player_cards[0][0]}, друга карта: {player_cards[1][0]}")
        print(f"Карта ділера: {dealer_cards[0][0]}, друга карта прихована")
        
        while True:
            total = calculate_total(player_cards)
            print(f"Ваші карти: {[card[0] for card in player_cards]}, сума: {total}")
            
            if total > 21:
                print("Перебір! Ви програли!")
                break
            
            if total == 21:
                print("Ви перемогли!")
                break

            choice = input("Взяти ще карту? (y/n): ").strip().lower()
            if choice == 'y':
                player_cards.append(deck.pop())
            else:
                break
        
        dealer_total = calculate_total(dealer_cards)
        print(f"Карти ділера: {[card[0] for card in dealer_cards]}, сума: {dealer_total}")
        
        while dealer_total < 17:
            dealer_cards.append(deck.pop())
            dealer_total = calculate_total(dealer_cards)
            print(f"Ділер бере карту: {dealer_cards[-1][0]}, нова сума: {dealer_total}")
        
        if total > 21 or (dealer_total <= 21 and dealer_total > total):
            print("Ділер переміг!")
        elif dealer_total == total:
            print("Нічія!")
        else:
            print("Ви перемогли!")
        
        again = input("Хочете зіграти ще раз? (y/n): ").strip().lower()
        if again != 'y':
            break

if __name__ == "__main__":
    play_blackjack()
