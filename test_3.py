import pygame
import sys
import time
from constants import *
from card_animation import *
from blackjack_deck import *

pygame.init()
clock = pygame.time.Clock()
gameDisplay = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('BlackJack')
FPS = 120
draw_sound = pygame.mixer.Sound("sounds/card-sounds-35956.mp3")
flip_sound = pygame.mixer.Sound("sounds/flipcard-91468.mp3")


def clear_text_area(x, y, width=200, height=50):
    pygame.draw.rect(gameDisplay, bg_colour, (x - width//2, y - height//2, width, height))

def text_objects(text, font, color=black):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def game_texts(text, x, y, color=black):
    TextSurf, TextRect = text_objects(text, textfont, color)
    TextRect.center = (x, y)
    gameDisplay.blit(TextSurf, TextRect)

def game_finish(text, x, y, color):
    TextSurf, TextRect = text_objects(text, game_end, color)
    TextRect.center = (x, y)
    gameDisplay.blit(TextSurf, TextRect)

def button(msg, x, y, w, h, ic, ac):
    mouse = pygame.mouse.get_pos()
    color = ac if x + w > mouse[0] > x and y + h > mouse[1] > y else ic
    pygame.draw.rect(gameDisplay, color, (x, y, w, h))
    
    TextSurf, TextRect = text_objects(msg, font)
    TextRect.center = ((x + (w / 2)), (y + (h / 2)))
    gameDisplay.blit(TextSurf, TextRect)

class Play:
    def __init__(self):
        self.deck = Deck()
        self.balance = 1000  # Початковий баланс гравця
        self.current_bet = 0
        self.insurance_bet = 0
        self.split_hands = []  # Руки після спліту
        self.active_hand_index = 0  # Яка рука зараз грає
        self.flip_animation = None
        self.reset_game()

    def place_bet(self, amount):
        if amount <= self.balance:
            self.current_bet += amount
            self.balance -= amount
            return True
        return False

    def win_bet(self, amount):
        self.balance += amount * 2  # Виплата 1:1

    def push_bet(self):
        self.balance += self.current_bet  # Повернення ставки

    def can_split(self):
        if len(self.player.card_img) == 2 and self.player.card_img[0][1] == self.player.card_img[1][1] and len(self.split_hands) == 0:
            return True
        return False

    def split_hand(self):
        if not self.can_split():
            return False

        # Зберігаємо початкову ставку
        original_bet = self.current_bet

        # Створюємо дві нові руки з окремими ставками
        self.split_hands = [Hand(bet=original_bet), Hand(bet=original_bet)]

        # Розподіляємо карти
        card1 = self.player.cards.pop()
        card2 = self.player.cards.pop()

        self.split_hands[0].add_card(card1)
        self.split_hands[1].add_card(card2)

        # Додаємо по одній новій карті кожній руці
        for hand in self.split_hands:
            card = self.deck.deal()
            hand.add_card(card)
            hand.calc_hand()

        # Віднімаємо ще одну ставку з балансу
        self.balance -= original_bet
        self.active_hand_index = 0

        return True
    def can_double_down(self):
        if self.split_hands:
            # Для розділених рук перевіряємо поточну активну руку
            current_hand = self.split_hands[self.active_hand_index]
            return len(current_hand.card_img) == 2 and self.balance >= current_hand.bet
        else:
         # Для звичайної гри перевіряємо основну руку
            return len(self.player.card_img) == 2 and self.balance >= self.current_bet
    
    def double_down(self):
        if not self.can_double_down():
            return

        if self.split_hands:
            # Для розділених рук
            current_hand = self.split_hands[self.active_hand_index]
            self.balance -= current_hand.bet  # Віднімаємо ставку
            current_hand.bet *= 2  # Подвоюємо ставку для поточної руки

            # Додаємо одну карту
            card = self.deck.deal()
            current_hand.add_card(card)
            current_hand.calc_hand()

            # Анімація взяття карти
            i = len(current_hand.card_img) - 1  # Індекс нової карти
            self.animate_card_draw(DECK_X, DECK_Y, 300 + i * 100, 450 + self.active_hand_index * 250, is_dealer=False)
            pygame.mixer.Sound.play(draw_sound)

            # Перевіряємо, чи потрібно переходити до наступної руки
            if self.active_hand_index < len(self.split_hands) - 1:
                self.active_hand_index += 1
            else:
                self.stand()
        else:
            # Звичайна логіка без розділення
            self.balance -= self.current_bet
            self.current_bet *= 2
            card = self.deck.deal()
            self.player.add_card(card)

            # Анімація взяття карти
            i = len(self.player.card_img) - 1
            self.animate_card_draw(DECK_X, DECK_Y, 300 + i * 100, 450, is_dealer=False)
            pygame.mixer.Sound.play(draw_sound)

            self.stand()

        self.update_display()

    def can_insurance(self):
        return (len(self.dealer.card_img) >= 1 and self.dealer.card_img[0][1] == 'A' and \
               len(self.player.card_img) == 2 and self.insurance_bet == 0 and \
           self.balance > 0) 
    
    def insurance(self, amount):
        if not self.can_insurance():
            raise ValueError("Insurance not available")
        if amount > min(self.current_bet // 2, self.balance):
            raise ValueError("Insurance amount too high")
        self.insurance_bet = amount
        self.balance -= amount
    
    def check_insurance(self):
        if self.insurance_bet > 0:
            if self.dealer.value == 21:  # Дилер має блекджек
                self.balance += self.insurance_bet * 2
            self.insurance_bet = 0

    def draw_deck_stack(self, screen):
        # Намалювати колоду
        pygame.draw.rect(screen, (200, 200, 200), 
                        (DECK_X, DECK_Y, DECK_WIDTH, DECK_HEIGHT))
        pygame.draw.rect(screen, (0, 0, 0), 
                        (DECK_X, DECK_Y, DECK_WIDTH, DECK_HEIGHT), 2)
        # Намалювати верхню карту 
        back_img = pygame.image.load('img/back.png').convert_alpha()
        back_img = pygame.transform.scale(back_img, (DECK_WIDTH, DECK_HEIGHT))
        screen.blit(back_img, (DECK_X, DECK_Y))
        # Лічильник карт, що залишилися
        remaining_text = f"{len(self.deck.cards)}"
        text_surf, text_rect = text_objects(remaining_text, pygame.font.SysFont(None, 30))
        text_rect.center = (DECK_X + DECK_WIDTH//2, DECK_Y + DECK_HEIGHT + 20)
        screen.blit(text_surf, text_rect)
    #Функція перезапуску гри
    def reset_game(self):
        self.dealer_flip_animation = None
        self.game_state = "waiting"  
        if self.deck.remaining_cards() < 20:
            self.deck.reset()
        self.dealer = Hand()
        self.player = Hand()
        self.split_hands = []        # Очистити розділені руки
        self.active_hand_index = 0   # Скинути індекс активної руки
        self.deck.shuffle()
        self.player_card_count = 0
        self.current_bet = 0
        self.insurance_bet = 0
        self.update_display()
        
    # функція оновленя інтерфейсу
    def update_display(self, show_dealer=False):
        gameDisplay.fill(bg_colour)
        pygame.draw.rect(gameDisplay, grey, pygame.Rect(0, 0, 285, 950))

        # Додаємо відображення стеку карт
        self.draw_deck_stack(gameDisplay)
        game_texts("Рука дилера:", 800, 90)
        #Рука дилера
        if show_dealer:
            for i, card in enumerate(self.dealer.card_img):
                if i == 1 and self.dealer_flip_animation:  # Друга карта дилера
                    self.dealer_flip_animation.draw(gameDisplay)
                    game_texts(f"Рахунок дилера: {self.dealer.value}", 800, 120)
                else:
                    card_img = pygame.image.load(f'img/{card}.png').convert_alpha()
                    gameDisplay.blit(card_img, (600 + i * 100, 150))
        else:
            # Перша карта дилера - лицевою стороною
            if len(self.dealer.card_img) > 0:
                card_img = pygame.image.load(f'img/{self.dealer.card_img[0]}.png').convert_alpha()
                gameDisplay.blit(card_img, (600, 150))

            # Друга карта дилера - анімація 
            if len(self.dealer.card_img) > 1:
                if self.dealer_flip_animation:
                    self.dealer_flip_animation.draw(gameDisplay)
                else:
                    card_img = pygame.image.load('img/back.png').convert_alpha()
                    gameDisplay.blit(card_img, (700, 150))
        
        if self.split_hands:
            for i, hand in enumerate(self.split_hands):
                y_offset = 450 + i * 250
                
                if self.game_state == "ended":
                    result = self.get_hand_result(hand)
                    status_text = f" ({result})"
                else:
                    status_text = ""
            
                # Відображаємо руку зі ставкою та результатом
                game_texts(f"Рука {i+1} (${hand.bet}){status_text}:", 800, y_offset - 30)
                for j, card in enumerate(hand.card_img):
                    card_img = pygame.image.load(f'img/{card}.png').convert()
                    gameDisplay.blit(card_img, (600 + j * 100, y_offset))
                if i == self.active_hand_index and self.game_state == "playing":
                    pygame.draw.rect(gameDisplay, (255, 255, 0), (590 , y_offset-5, 120 + j * 100, 160), 2)
                # Відображаємо значення руки
                hand.calc_hand()
                game_texts(f"Твій рахунок: {hand.value}",800, y_offset + 170,
                           green if self.player.value == 21 else red if self.player.value > 21 else black)
        else:
            # Звичайне відображення руки гравця
            game_texts("Твоя рука:", 800, 400)
            for i, card in enumerate(self.player.card_img):
                card_img = pygame.image.load(f'img/{card}.png').convert()
                gameDisplay.blit(card_img, (600 + i * 100, 450))
                        # Рахунок гравця
                self.player.calc_hand()
                clear_text_area(800, 650)
                game_texts(f"Твій рахунок: {self.player.value}", 800, 650, 
                          green if self.player.value == 21 else red if self.player.value > 21 else black)

        # Відображаємо баланс і ставку
        game_texts(f"Balance: ${self.balance:>5}", 142, 20)
        game_texts(f"Bet: ${self.current_bet:>5}", 142, 60)
        if self.game_state == "waiting":
            button("Bet 10", 40, 100, 150, 40, light_slat, dark_slat)
            button("Bet 50", 40, 150, 150, 40, light_slat, dark_slat)
            button("Bet 100", 40, 200, 150, 40, light_slat, dark_slat)

        


        # Кнопки
        button("Роздати", 40, 350, 150, 50, light_slat, dark_slat)
        if self.game_state == "playing":
            button("Додати карту", 40, 450, 150, 50, light_slat, dark_slat)
            button("Зупинитися", 40, 550, 150, 50, light_slat, dark_slat)
            if self.can_double_down():
                button("Подвоїти", 40, 650, 150, 40, light_slat, dark_slat)
            
            if self.can_split():
                button("Розділити", 40, 750, 150, 40, light_slat, dark_slat)
            if self.split_hands:
                button("Переключити руку", 40, 260, 200, 30, light_slat, dark_slat)
        button("Вихід", 40, 850, 150, 50, light_slat, dark_red)

        pygame.display.update()
    #Функція роздачі
    def deal(self):
        if self.game_state == "playing":
            return
        

        if self.balance <= 0:
            self.show_result("Game Over! No funds", red)
            return
        self.dealer.clear()
        self.player.clear()
        self.dealer_flip_animation = None
        # Перевіряємо, чи достатньо карт для роздачі
        if self.deck.remaining_cards() < 15:  
            self.deck.reset()

        for i in range(2):
            # Анімація взяття карти для дилера
            if i == 0:
                card = ('S', '10')  # Перша карта дилера - Туз
            elif i == 1:
                card = ('S', 'A')  # Друга карта дилера - 10
            else:
                card = self.deck.deal()
            self.animate_card_draw(DECK_X, DECK_Y, 600 + i * 100, 150, is_dealer=True)
            pygame.mixer.Sound.play(draw_sound)
            self.dealer.add_card(card)

            # Анімація взяття карти для гравця
            if i == 0:
                player_card = ('H', '10')  # Перша карта гравця - Туз
            elif i == 1:
                player_card = ('H', 'A')  # Друга карта гравця - 10
            else:
                player_card = self.deck.deal()

            self.animate_card_draw(DECK_X, DECK_Y, 600 + i * 100, 450, is_dealer=False)
            pygame.mixer.Sound.play(draw_sound)
            self.player.add_card(player_card)

        self.player_card_count = 2
        self.game_state = "playing"

        if self.can_insurance():
            self.show_insurance_option()
    
        self.update_display()

        # Анімація перевороту карти ділера
        if len(self.dealer.card_img) > 1:
            card_name = self.dealer.card_img[1]
            final_card_path = f'img/{card_name}.png'

            self.dealer_flip_animation = CardFlipAnimation(x=700, y=150, final_card_image_path=final_card_path, scale=1)

        self.check_blackjack()
        self.update_display()
    # Функція перевірки на блекджек
    def check_blackjack(self):
        self.dealer.calc_hand()
        self.player.calc_hand()

        player_blackjack = (len(self.player.cards) == 2 and self.player.value == 21)
        dealer_blackjack = (len(self.dealer.cards) == 2 and 
                   ((self.dealer.cards[0][1] == 'A' and self.dealer.cards[1][1] in ['10', 'J', 'Q', 'K']) or
                    (self.dealer.cards[1][1] == 'A' and self.dealer.cards[0][1] in ['10', 'J', 'Q', 'K'])))


        if player_blackjack or dealer_blackjack:
            if self.dealer_flip_animation:
                self.dealer_flip_animation.start_animation()
            while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
                self.dealer_flip_animation.update()
                self.update_display()
                pygame.time.delay(10)
                pygame.display.update()

            self.game_state = "ended"
            self.check_insurance()
            if player_blackjack and dealer_blackjack:
                message, color = "Блекджек у обох!", grey
                self.push_bet()
            elif player_blackjack:
                message, color = "У тебе блекджек!", green
                self.balance += int(self.current_bet * 2.5)  # Виплата 3:2 за блекджек
            else:
                message, color = "У дилера блекджек!", red

            self.show_result(message, color)


    def show_insurance_option(self):
        # Створюємо поверх для затемнення
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Напівпрозорий чорний

        # Відображаємо overlay
        gameDisplay.blit(overlay, (0, 0))

        # Створюємо вікно для пропозиції страхування
        pygame.draw.rect(gameDisplay, (220, 220, 220), (300, 300, 560, 250))
        pygame.draw.rect(gameDisplay, black, (300, 300, 560, 250), 2)

        # Текст повідомлення
        game_texts("Дилер має туза. Страхування?", 580, 315)
        game_texts(f"Ціна страховки: ${min(self.current_bet // 2, self.balance)}", 580, 360)

        # Кнопкиі
        button("Страхувати", 485, 400, 150, 40, light_slat, dark_slat)
        button("Не страхувати", 460, 460, 200, 40, light_slat, dark_slat)

        pygame.display.update()

        # Обробка вибору гравця
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()

                    # Кнопка "Страхувати"
                    if 485 <= mouse_pos[0] <= 635 and 400 <= mouse_pos[1] <= 440:
                        insurance_amount = min(self.current_bet // 2, self.balance)
                        self.insurance(insurance_amount)
                        waiting_for_input = False

                    # Кнопка "Не страхувати"
                    elif 460 <= mouse_pos[0] <= 660 and 460 <= mouse_pos[1] <= 500:
                        waiting_for_input = False

        # Оновлюємо екран після вибору
        self.update_display()

    def animate_card_draw(self, start_x, start_y, end_x, end_y, is_dealer):
        # Створюємо тимчасовий спрайт для анімації
        back_img = pygame.image.load('img/back.png').convert_alpha()
        back_img = pygame.transform.scale(back_img, (DECK_WIDTH, DECK_HEIGHT))

        steps = 20  # Кількість кроків анімації
        for i in range(steps):
            # Проміжні координати
            x = start_x + (end_x - start_x) * i / steps
            y = start_y + (end_y - start_y) * i / steps

            # Оновлюємо екран
            self.update_display()

            # Малюємо карту, що рухається
            gameDisplay.blit(back_img, (x, y))
            pygame.display.update()
            pygame.time.delay(10)
    # Функція добору карт
    def hit(self):
        if self.game_state != "playing":
            return

        if self.split_hands:
            # Логіка для розділених рук
            current_hand = self.split_hands[self.active_hand_index]

            # Перевіряємо наявність карт у колоді
            if self.deck.remaining_cards() == 0:
                self.deck.reset()

            card = self.deck.deal()
            if card is None:
                return

            # Анімація взяття карти
            i = len(current_hand.card_img)
            self.animate_card_draw(DECK_X, DECK_Y, 600 + i * 100, 450 + self.active_hand_index * 250, is_dealer=False)
            pygame.mixer.Sound.play(draw_sound)

            # Додаємо карту до поточної руки
            current_hand.add_card(card)
            current_hand.calc_hand()

            # Перевірка на перебір
            if current_hand.value > 21:
                if len(self.split_hands) > self.active_hand_index + 1:
                    # Переходимо до наступної руки
                    self.active_hand_index += 1
                else:
                    # Всі руки завершено
                    self.stand()
            elif current_hand.value == 21:
                # Автоматично зупиняємося на 21
                if len(self.split_hands) > self.active_hand_index + 1:
                    self.active_hand_index += 1
                else:
                    self.stand()
        else:
            # Звичайна логіка без розділення
            if self.deck.remaining_cards() == 0:
                self.deck.reset()

            card = self.deck.deal()
            if card is None:
                return

            i = len(self.player.card_img)
            self.animate_card_draw(DECK_X, DECK_Y, 600 + i * 100, 450, is_dealer=False)
            pygame.mixer.Sound.play(draw_sound)
            self.player.add_card(card)
            self.player.calc_hand()

            if self.player.value > 21:
                self.game_state = "ended"
                self.show_result("Ти перебрав!", red)
            elif self.player.value == 21:
                self.stand()

        self.update_display()

    def change_hand(self):

        self.active_hand_index += 1

    def get_hand_result(self, hand):
        hand.calc_hand()
        self.dealer.calc_hand()
        
        if hand.value > 21:
            return "Програш (перебір)"
        elif self.dealer.value > 21:
            return "Виграш (дилер перебрав)"
        elif hand.value > self.dealer.value:
            return "Виграш"
        elif hand.value == self.dealer.value:
            return "Нічия"
        else:
            return "Програш"

    # Функція зупинки роздачі
    def stand(self):
        if self.game_state != "playing":
            return

        if self.split_hands:
            # Для розділених рук перевіряємо, чи є ще руки
            if self.active_hand_index < len(self.split_hands) - 1:
                self.active_hand_index += 1
                return

        # Якщо всі руки завершено або це звичайна гра
        self.game_state = "ended"

        # Перевертаємо карти дилера
        if self.dealer_flip_animation:
            pygame.mixer.Sound.play(flip_sound)
            self.dealer_flip_animation.start_animation()
            while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
                self.dealer_flip_animation.update()
                self.update_display()
                pygame.time.delay(10)
                pygame.display.update()

        # Оновлюємо екран під час анімації
        while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
            self.dealer_flip_animation.update()
            self.update_display()
            pygame.time.delay(10)
            pygame.display.update()

        # Дилер добирає карти
        self.dealer.calc_hand()
        i = len(self.dealer.card_img)
        while self.dealer.value < 17 :
            self.animate_card_draw(DECK_X, DECK_Y, 600 + i * 100, 150, is_dealer=True)
            pygame.mixer.Sound.play(draw_sound)
            self.dealer.add_card(self.deck.deal())
            self.dealer.calc_hand()
            i += 1
            pygame.time.delay(10)

        # Визначаємо результати
        dealer_value = self.dealer.value

        if self.split_hands:
            # Обробка розділених рук
            for i, hand in enumerate(self.split_hands):
                hand.calc_hand()
                result = self.get_hand_result(hand)

                if "Виграш" in result:
                    self.balance += hand.bet * 2
                elif "Нічия" in result:
                    self.balance += hand.bet

                # Оновлюємо відображення
                self.update_display(show_dealer=True)
                time.sleep(1)  # Невелика затримка між результатами
        else:
            # Звичайна гра без розділення
            self.player.calc_hand()
            result = self.get_hand_result(self.player)

            if "Виграш" in result:
                self.win_bet(self.current_bet)
            elif "Нічия" in result:
                self.push_bet()

        self.show_result("Гра завершена!", grey)
        self.update_display(show_dealer=True)

    def show_result(self, message, color):
        # Оновлюємо екран з показом всіх карт дилера
        self.update_display(show_dealer=True)

        # Відображаємо повідомлення про результат
        game_finish(message, 905, 325, color)


        pygame.display.update()
        time.sleep(10)  # Затримка для читання результату

        self.reset_game()
        self.update_display()





    def exit(self):
        pygame.quit()
        sys.exit()

# Головна петля
play_blackjack = Play()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            if 30 <= mouse_pos[0] <= 180:
                if 100 <= mouse_pos[1] <= 140 and play_blackjack.game_state == "waiting":
                    play_blackjack.place_bet(10)
                elif 150 <= mouse_pos[1] <= 190 and play_blackjack.game_state == "waiting":
                    play_blackjack.place_bet(50)
                elif 200 <= mouse_pos[1] <= 250 and play_blackjack.game_state == "waiting":
                    play_blackjack.place_bet(100)
                elif 350 <= mouse_pos[1] <= 400:
                    play_blackjack.deal()
                elif 450 <= mouse_pos[1] <= 500 and play_blackjack.game_state == "playing":
                    play_blackjack.hit()
                elif 550 <= mouse_pos[1] <= 600 and play_blackjack.game_state == "playing":
                    play_blackjack.stand()
                elif 650 <= mouse_pos[1] <= 700 and play_blackjack.game_state == "playing":
                    play_blackjack.double_down()
                elif 750 <= mouse_pos[1] <= 800 and play_blackjack.game_state == "playing":
                    play_blackjack.split_hand()
                elif 260 <= mouse_pos[1] <= 290 and play_blackjack.game_state == "playing":
                    play_blackjack.change_hand()
                elif 850 <= mouse_pos[1] <= 900:
                    play_blackjack.exit()
    
    # Оновлюємо екран
    play_blackjack.update_display(play_blackjack.game_state == "ended")  # Показуємо всі карти, якщо гра закінчена
    clock.tick(60)


pygame.quit()
sys.exit()



