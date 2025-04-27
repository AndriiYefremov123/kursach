import pygame
import sys
import time
import random
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
        self.reset_game()
        self.flip_animation = None

    def draw_deck_stack(self, screen):
        # Draw the base of the stack (bottom card)
        pygame.draw.rect(screen, (200, 200, 200), 
                        (DECK_X, DECK_Y, DECK_WIDTH, DECK_HEIGHT))
        pygame.draw.rect(screen, (0, 0, 0), 
                        (DECK_X, DECK_Y, DECK_WIDTH, DECK_HEIGHT), 2)
        # Draw the top card (back side up)
        back_img = pygame.image.load('img/back.png').convert_alpha()
        back_img = pygame.transform.scale(back_img, (DECK_WIDTH, DECK_HEIGHT))
        screen.blit(back_img, (DECK_X, DECK_Y))
        # Display remaining cards count
        remaining_text = f"{len(self.deck.cards)}"
        text_surf, text_rect = text_objects(remaining_text, pygame.font.SysFont(None, 30))
        text_rect.center = (DECK_X + DECK_WIDTH//2, DECK_Y + DECK_HEIGHT + 20)
        screen.blit(text_surf, text_rect)

    def reset_game(self):
        self.dealer_flip_animation = None
        self.game_state = "waiting"  # waiting, playing, ended
        if self.deck.remaining_cards() < 20:
            self.deck.reset()
        self.deck = Deck()
        self.dealer = Hand()
        self.player = Hand()
        self.deck.shuffle()
        self.player_card_count = 0
        self.update_display()
        

    def update_display(self, show_dealer=False):
        gameDisplay.fill(bg_colour)
        pygame.draw.rect(gameDisplay, grey, pygame.Rect(0, 0, 220, 850))

        # Додаємо відображення стеку карт
        self.draw_deck_stack(gameDisplay)


        game_texts("Рука дилера:", 500, 90)
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


        # Player's cards
        game_texts("Твоя рука:", 500, 400)
        for i, card in enumerate(self.player.card_img):
            card_img = pygame.image.load(f'img/{card}.png').convert()
            gameDisplay.blit(card_img, (300 + i * 100, 450))
        
        # Player's total
        self.player.calc_hand()
        clear_text_area(500, 650)
        game_texts(f"Твій рахунок: {self.player.value}", 500, 650, 
                  green if self.player.value == 21 else red if self.player.value > 21 else black)

        # Buttons
        button("Роздати", 30, 100, 150, 50, light_slat, dark_slat)
        if self.game_state == "playing":
            button("Додати карту", 30, 200, 150, 50, light_slat, dark_slat)
            button("Зупинитися", 30, 300, 150, 50, light_slat, dark_slat)
        button("Вихід", 30, 500, 150, 50, light_slat, dark_red)

        pygame.display.update()

    def deal(self):
        if self.game_state == "playing":
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

        # Set up flip animation for dealer's second card
        if len(self.dealer.card_img) > 1:
            card_name = self.dealer.card_img[1]
            final_card_path = f'img/{card_name}.png'

            self.dealer_flip_animation = CardFlipAnimation(x=400, y=150, final_card_image_path=final_card_path, scale=1)

        self.check_blackjack()
        self.update_display()

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
        
        # Dealer draws cards
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
        
        # Determine result
        self.dealer.calc_hand()
        self.player.calc_hand()
        
        if self.dealer.value > 21:
            result, color = "Дилер перебрав! Ти переміг!", green
        elif self.player.value > self.dealer.value:
            result, color = "Ти переміг!", green
        elif self.player.value < self.dealer.value:
            result, color = "Дилер переміг!", red
        else:
            result, color = "Це нічия!", grey
        
        self.show_result(result, color)

    def show_result(self, message, color):
        # Оновлюємо екран з показом всіх карт дилера
        self.update_display(show_dealer=True)

        # Відображаємо повідомлення про результат
        game_finish(message, 605, 325, color)


        pygame.display.update()
        time.sleep(2)  # Затримка для читання результату


    def exit(self):
        pygame.quit()
        sys.exit()

# Main game loop
play_blackjack = Play()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            if 30 <= mouse_pos[0] <= 180:
                if 100 <= mouse_pos[1] <= 150:
                    play_blackjack.deal()
                elif 200 <= mouse_pos[1] <= 250 and play_blackjack.game_state == "playing":
                    play_blackjack.hit()
                elif 300 <= mouse_pos[1] <= 350 and play_blackjack.game_state == "playing":
                    play_blackjack.stand()
                elif 500 <= mouse_pos[1] <= 550:
                    play_blackjack.exit()
    
    # Оновлюємо екран
    play_blackjack.update_display(play_blackjack.game_state == "ended")  # Показуємо всі карти, якщо гра закінчена
    clock.tick(60)

pygame.quit()
sys.exit()