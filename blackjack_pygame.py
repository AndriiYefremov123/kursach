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

        # Знімаємо додаткову ставку
        self.balance -= self.current_bet

        # Створюємо дві нові руки
        self.split_hands = [
            Hand(),
            Hand()
        ]

        # Розподіляємо карти
        card1 = self.player.cards.pop()
        card2 = self.player.cards.pop()

        self.split_hands[0].add_card(card1)
        self.split_hands[1].add_card(card2)

        # Додаємо нові карти до кожної руки
        for hand in self.split_hands:
            card = self.deck.deal()
            hand.add_card(card)
            hand.calc_hand()  # Обчислюємо значення руки
    
        self.active_hand_index = 0
        return True
    def can_double_down(self):
        return len(self.player.card_img) == 2 and self.balance >= self.current_bet
    
    def double_down(self):
        if self.can_double_down():
            self.balance -= self.current_bet
            self.current_bet *= 2
            # Гравець отримує одну карту і автоматично стає
            card = self.deck.deal()
            self.player.add_card(card)
            self.stand()

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
        self.deck.shuffle()
        self.player_card_count = 0
        self.current_bet = 0
        self.insurance_bet = 0
        self.update_display()
        
    # функція оновленя інтерфейсу
    def update_display(self, show_dealer=False):
        gameDisplay.fill(bg_colour)
        pygame.draw.rect(gameDisplay, grey, pygame.Rect(0, 0, 280, 950))

        # Додаємо відображення стеку карт
        self.draw_deck_stack(gameDisplay)
        game_texts("Рука дилера:", 500, 90)
        #Рука дилера
        if show_dealer:
            for i, card in enumerate(self.dealer.card_img):
                if i == 1 and self.dealer_flip_animation:  # Друга карта дилера
                    self.dealer_flip_animation.draw(gameDisplay)
                    game_texts(f"Рахунок дилера: {self.dealer.value}", 500, 120)
                else:
                    card_img = pygame.image.load(f'img/{card}.png').convert_alpha()
                    gameDisplay.blit(card_img, (300 + i * 100, 150))
        else:
            # Перша карта дилера - лицевою стороною
            if len(self.dealer.card_img) > 0:
                card_img = pygame.image.load(f'img/{self.dealer.card_img[0]}.png').convert_alpha()
                gameDisplay.blit(card_img, (300, 150))

            # Друга карта дилера - анімація 
            if len(self.dealer.card_img) > 1:
                if self.dealer_flip_animation:
                    self.dealer_flip_animation.draw(gameDisplay)
                else:
                    card_img = pygame.image.load('img/back.png').convert_alpha()
                    gameDisplay.blit(card_img, (400, 150))
        
        if self.split_hands:
            for i, hand in enumerate(self.split_hands):
                y_offset = 450 + i * 200
                game_texts(f"Split Hand {i+1}:", 500, y_offset - 30)
                for j, card in enumerate(hand.card_img):
                    card_img = pygame.image.load(f'img/{card}.png').convert()
                    gameDisplay.blit(card_img, (300 + j * 100, y_offset))

                # Відображаємо значення руки
                hand.calc_hand()
                game_texts(f"Value: {hand.value}", 500, y_offset + 70)
        else:
            # Звичайне відображення руки гравця
            game_texts("Твоя рука:", 500, 400)
            for i, card in enumerate(self.player.card_img):
                card_img = pygame.image.load(f'img/{card}.png').convert()
                gameDisplay.blit(card_img, (300 + i * 100, 450))

        # Відображаємо баланс і ставку
        game_texts(f"Balance: ${self.balance:>5}", 142, 20)
        game_texts(f"Bet: ${self.current_bet:>5}", 142, 60)
        if self.game_state == "waiting":
            button("Bet 10", 40, 100, 150, 40, light_slat, dark_slat)
            button("Bet 50", 40, 150, 150, 40, light_slat, dark_slat)
            button("Bet 100", 40, 200, 150, 40, light_slat, dark_slat)

        
        # Рахунок гравця
        self.player.calc_hand()
        clear_text_area(500, 650)
        game_texts(f"Твій рахунок: {self.player.value}", 500, 650, 
                  green if self.player.value == 21 else red if self.player.value > 21 else black)

        # Кнопки
        button("Роздати", 40, 350, 150, 50, light_slat, dark_slat)
        if self.game_state == "playing":
            button("Додати карту", 40, 450, 150, 50, light_slat, dark_slat)
            button("Зупинитися", 40, 550, 150, 50, light_slat, dark_slat)
            if self.can_double_down():
                button("Double", 40, 650, 150, 40, light_slat, dark_slat)
            
            if self.can_split():
                button("Split", 40, 750, 150, 40, light_slat, dark_slat)
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
            card = self.deck.deal()
            if card is None:
                return
            self.animate_card_draw(DECK_X, DECK_Y, 300 + i * 100, 150, is_dealer=True)
            pygame.mixer.Sound.play(draw_sound)
            self.dealer.add_card(card)

            # Анімація взяття карти для гравця
            card = self.deck.deal()
            if card is None:
                return
            self.animate_card_draw(DECK_X, DECK_Y, 300 + i * 100, 450, is_dealer=False)
            pygame.mixer.Sound.play(draw_sound)
            self.player.add_card(card)

        self.player_card_count = 2
        self.game_state = "playing"

        if self.can_insurance():
            self.show_insurance_option()
    
        self.update_display()

        # Анімація перевороту карти ділера
        if len(self.dealer.card_img) > 1:
            card_name = self.dealer.card_img[1]
            final_card_path = f'img/{card_name}.png'

            self.dealer_flip_animation = CardFlipAnimation(x=400, y=150, final_card_image_path=final_card_path, scale=1)

        self.check_blackjack()
        self.update_display()
    # Функція перевірки на блекджек
    def check_blackjack(self):
        self.dealer.calc_hand()
        self.player.calc_hand()
        
        if self.player.value == 21 or self.dealer.value == 21:
            if self.dealer_flip_animation:
                self.dealer_flip_animation.start_animation()
            while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
                self.dealer_flip_animation.update()
                self.update_display()
                pygame.time.delay(10)
                pygame.display.update()
            self.game_state = "ended"
            if self.player.value == 21 and self.dealer.value == 21:
                if self.dealer_flip_animation:
                    pygame.mixer.Sound.play(flip_sound)
                    self.dealer_flip_animation.start_animation()
                while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
                    self.dealer_flip_animation.update()
                    self.update_display()
                    pygame.time.delay(10)
                    pygame.display.update()
                message, color = "Блекджек у обох!", grey
            elif self.player.value == 21:
                if self.dealer_flip_animation:
                    pygame.mixer.Sound.play(flip_sound)
                    self.dealer_flip_animation.start_animation()
                while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
                    self.dealer_flip_animation.update()
                    self.update_display()
                    pygame.time.delay(10)
                    pygame.display.update()
                message, color = "У тебе блекджек!", green
            else:
                if self.dealer_flip_animation:
                    pygame.mixer.Sound.play(flip_sound)
                    self.dealer_flip_animation.start_animation()
                while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
                    self.dealer_flip_animation.update()
                    self.update_display()
                    pygame.time.delay(10)
                    pygame.display.update()
                message, color = "У дилера блекджек!", red
            
            self.show_result(message, color)
    #Функція для створеня анімації роздачі карти 

    def show_insurance_option(self):
        # Створюємо поверх для затемнення
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Напівпрозорий чорний

        # Відображаємо overlay
        gameDisplay.blit(overlay, (0, 0))

        # Створюємо вікно для пропозиції страхування
        pygame.draw.rect(gameDisplay, (220, 220, 220), (300, 300, 450, 200))
        pygame.draw.rect(gameDisplay, black, (300, 300, 450, 200), 2)

        # Текст повідомлення
        game_texts("Дилер має туза. Страхування?", 525, 330)
        game_texts(f"Максимальна ставка: ${min(self.current_bet // 2, self.balance)}", 525, 360)

        # Кнопки
        button("Страхувати (1/2 ставки)", 350, 400, 200, 40, light_slat, dark_slat)
        button("Продовжити", 550, 400, 200, 40, light_slat, dark_slat)

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
                    if 350 <= mouse_pos[0] <= 550 and 400 <= mouse_pos[1] <= 440:
                        insurance_amount = min(self.current_bet // 2, self.balance)
                        self.insurance(insurance_amount)
                        waiting_for_input = False

                    # Кнопка "Продовжити"
                    elif 550 <= mouse_pos[0] <= 750 and 400 <= mouse_pos[1] <= 440:
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
        
        # Перевіряємо, чи є карти в колоді
        if self.deck.remaining_cards() == 0:
            self.deck.reset()
        
        card = self.deck.deal()
        if card is None:
            return
        
        i = len(self.player.card_img)
        self.animate_card_draw(DECK_X, DECK_Y, 300 + i * 100, 450, is_dealer=False)
        pygame.mixer.Sound.play(draw_sound)
        self.player.add_card(card)
        self.player_card_count += 1
        self.player.calc_hand()
        # Перевірка чи перебрав гравець
        if self.player.value > 21:
            if self.dealer_flip_animation:
                pygame.mixer.Sound.play(flip_sound)
                self.dealer_flip_animation.start_animation()

            while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
                self.dealer_flip_animation.update()
                self.update_display()
                pygame.time.delay(10)
                pygame.display.update()
            self.game_state = "ended"
            self.show_result("Ти перебрав!", red)
        elif self.player.value == 21:
            self.stand()
        else:
            self.update_display()
    # Функція зупинки роздачі
    def stand(self):
        if self.game_state != "playing":
            return
            
        self.game_state = "ended"
        
        # Запускаємо анімацію перевороту
        if self.dealer_flip_animation:
            pygame.mixer.Sound.play(flip_sound)
            self.dealer_flip_animation.start_animation()
        
        # Оновлюємо екран під час анімації
        while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
            self.dealer_flip_animation.update()
            self.update_display()
            pygame.time.delay(10)
            pygame.display.update()
        
        # Анімація роздачі карт Дилеру
        self.dealer.calc_hand()
        i = 1
        while self.dealer.value < 17 and len(self.dealer.card_img) < 5:
            self.animate_card_draw(DECK_X, DECK_Y, 400 + i * 100, 150, is_dealer=True)
            pygame.mixer.Sound.play(draw_sound)
            self.dealer.add_card(self.deck.deal())
            self.dealer.calc_hand()
            self.update_display()
            i += 1
            pygame.time.delay(10)
        
        # Кінцевий результат 
        self.dealer.calc_hand()
        self.player.calc_hand()
        
        if self.dealer.value > 21:
            result, color = "Дилер перебрав! Ти переміг!", green
            self.win_bet(self.current_bet)
        elif self.player.value > self.dealer.value:
            result, color = "Ти переміг!", green
            self.win_bet(self.current_bet)
        elif self.player.value < self.dealer.value:
            result, color = "Дилер переміг!", red
        else:
            result, color = "Це нічия!", grey
            self.push_bet()
        
        self.show_result(result, color)

    def show_result(self, message, color):
        # Оновлюємо екран з показом всіх карт дилера
        self.update_display(show_dealer=True)

        # Відображаємо повідомлення про результат
        game_finish(message, 605, 325, color)


        pygame.display.update()
        time.sleep(2)  # Затримка для читання результату

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
                elif 850 <= mouse_pos[1] <= 900:
                    play_blackjack.exit()
    
    # Оновлюємо екран
    play_blackjack.update_display(play_blackjack.game_state == "ended")  # Показуємо всі карти, якщо гра закінчена
    clock.tick(60)


pygame.quit()
sys.exit()


