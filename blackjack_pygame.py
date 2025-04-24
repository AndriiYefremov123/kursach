import pygame
import sys
import time
from constants import *
from blackjack_deck import *

pygame.init()
clock = pygame.time.Clock()
gameDisplay = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('BlackJack')
FPS = 120


class CardFlipAnimation:
    def __init__(self, x, y, final_card_image_path, scale=1):
        self.x = x
        self.y = y
        self.scale = scale
        self.final_card_image = pygame.image.load(final_card_image_path).convert_alpha()
        self.final_card_image = pygame.transform.scale(self.final_card_image, 
                                                     (int(self.final_card_image.get_width() * scale), 
                                                      int(self.final_card_image.get_height() * scale)))
        
        # Завантаження кадрів анімації
        self.animation_frames = []
        for i in range(2):  # Припустимо, 10 кадрів анімації
            try:
                frame_path = f'Card Flip/{i}.png'  # Приклад: flip_0.png, flip_1.png, ...
                img = pygame.image.load(frame_path).convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), 
                                                 int(img.get_height() * scale)))
                self.animation_frames.append(img)
            except:
                print(f"Не вдалося завантажити кадр анімації: {frame_path}")
                continue
        
        if not self.animation_frames:
            # Якщо немає кадрів анімації, створюємо просту анімацію
            back_img = pygame.image.load('img/back.png').convert_alpha()
            back_img = pygame.transform.scale(back_img, 
                                           (int(back_img.get_width() * scale), 
                                            int(back_img.get_height() * scale)))
            self.animation_frames = [back_img, self.final_card_image]
        
        self.current_frame = 0
        self.animation_speed = 5  # Чим менше, тим швидше
        self.animation_counter = 0
        self.is_animating = False
        self.animation_complete = False

    def start_animation(self):
        if not self.is_animating and not self.animation_complete:
            self.is_animating = True
            self.current_frame = 0
            self.animation_counter = 0
            self.animation_complete = False

    def update(self):
        if self.is_animating:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.current_frame += 1
                
                if self.current_frame >= len(self.animation_frames):
                    self.is_animating = False
                    self.animation_complete = True
                else:
                    # Плавний перехід між кадрами
                    pass

    def draw(self, screen):
        if self.animation_complete:
            # Після завершення анімації показуємо фінальну карту
            screen.blit(self.final_card_image, (self.x, self.y))
        elif self.is_animating:
            # Під час анімації показуємо поточний кадр
            screen.blit(self.animation_frames[self.current_frame], (self.x, self.y))
        else:
            # До початку анімації показуємо зворотню сторону карти
            screen.blit(self.animation_frames[0], (self.x, self.y))
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
        self.reset_game()
        self.flip_animation = None

    def reset_game(self):
        self.deck = Deck()
        self.dealer = Hand()
        self.player = Hand()
        self.deck.shuffle()
        self.player_card_count = 0
        self.game_state = "waiting"  # waiting, playing, ended
        self.update_display()
        self.dealer_flip_animation = None

    def update_display(self, show_dealer=False):
        gameDisplay.fill(bg_colour)
        pygame.draw.rect(gameDisplay, grey, pygame.Rect(0, 0, 220, 850))
        
        game_texts("Dealer's hand:", 500, 90)
        if show_dealer:
            for i, card in enumerate(self.dealer.card_img):
                if i == 1 and self.dealer_flip_animation:  # Друга карта дилера
                    self.dealer_flip_animation.draw(gameDisplay)
                    game_texts(f"Dealer's total: {self.dealer.value}", 500, 120)
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
        game_texts("Your hand:", 500, 400)
        for i, card in enumerate(self.player.card_img):
            card_img = pygame.image.load(f'img/{card}.png').convert()
            gameDisplay.blit(card_img, (300 + i * 100, 450))
        
        # Player's total
        self.player.calc_hand()
        clear_text_area(500, 650)
        game_texts(f"Your total: {self.player.value}", 500, 650, 
                  green if self.player.value == 21 else red if self.player.value > 21 else black)

        # Buttons
        button("Deal", 30, 100, 150, 50, light_slat, dark_slat)
        if self.game_state == "playing":
            button("Hit", 30, 200, 150, 50, light_slat, dark_slat)
            button("Stand", 30, 300, 150, 50, light_slat, dark_slat)
        button("EXIT", 30, 500, 150, 50, light_slat, dark_red)

        pygame.display.update()

    def deal(self):
        if self.game_state == "playing":
            return
            
        self.reset_game()
        for _ in range(2):
            self.dealer.add_card(self.deck.deal())
            self.player.add_card(self.deck.deal())
        
        self.player_card_count = 2
        self.game_state = "playing"
        
        # Set up flip animation for dealer's second card
        if len(self.dealer.card_img) > 1:
            card_name = self.dealer.card_img[1]  # Назва карти, що випала дилеру
            final_card_path = f'img/{card_name}.png'
            self.dealer_flip_animation = CardFlipAnimation(x=400, y=150,final_card_image_path=final_card_path,scale=1)
        
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
                    self.dealer_flip_animation.start_animation()
                while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
                    self.dealer_flip_animation.update()
                    self.update_display()
                    pygame.time.delay(10)
                    pygame.display.update()
                message, color = "Both with BlackJack!", grey
            elif self.player.value == 21:
                if self.dealer_flip_animation:
                    self.dealer_flip_animation.start_animation()
                while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
                    self.dealer_flip_animation.update()
                    self.update_display()
                    pygame.time.delay(10)
                    pygame.display.update()
                message, color = "You got BlackJack!", green
            else:
                if self.dealer_flip_animation:
                    self.dealer_flip_animation.start_animation()
                while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
                    self.dealer_flip_animation.update()
                    self.update_display()
                    pygame.time.delay(10)
                    pygame.display.update()
                message, color = "Dealer has BlackJack!", red
            
            self.show_result(message, color)

    def hit(self):
        if self.game_state != "playing":
            return
            
        self.player.add_card(self.deck.deal())
        self.player_card_count += 1
        self.player.calc_hand()
        
        if self.player.value > 21:
            if self.dealer_flip_animation:
                self.dealer_flip_animation.start_animation()
            while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
                self.dealer_flip_animation.update()
                self.update_display()
                pygame.time.delay(10)
                pygame.display.update()
            self.game_state = "ended"
            self.show_result("You Busted!", red)

            
            
        elif self.player.value == 21:
            self.update_display()
            play_blackjack.stand()
        else:
            self.update_display()

    def stand(self):
        if self.game_state != "playing":
            return
            
        self.game_state = "ended"
        
        # Запускаємо анімацію перевороту
        if self.dealer_flip_animation:
            self.dealer_flip_animation.start_animation()
        
        # Оновлюємо екран під час анімації
        while self.dealer_flip_animation and self.dealer_flip_animation.is_animating:
            self.dealer_flip_animation.update()
            self.update_display()
            pygame.time.delay(10)
            pygame.display.update()
        
        # Dealer draws cards
        self.dealer.calc_hand()
        while self.dealer.value < 17 and len(self.dealer.card_img) < 5:
            self.dealer.add_card(self.deck.deal())
            self.dealer.calc_hand()
        
        # Determine result
        self.dealer.calc_hand()
        self.player.calc_hand()
        
        if self.player.value > 21:
            result, color = "You Busted!", red
        elif self.dealer.value > 21:
            result, color = "Dealer Busted! You Win!", green
        elif self.player.value > self.dealer.value:
            result, color = "You Win!", green
        elif self.player.value < self.dealer.value:
            result, color = "Dealer Wins!", red
        else:
            result, color = "It's a Tie!", grey
        
        self.show_result(result, color)

    def show_result(self, message, color):
        self.update_display(show_dealer=True)
        game_finish(message, 550, 315, color)
        pygame.display.update()
        time.sleep(2)
        game_texts("Press Deal to play again", 200, 80)
        pygame.display.update()

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
            
            # Check button clicks
            if 30 <= mouse_pos[0] <= 180:
                if 100 <= mouse_pos[1] <= 150:
                    play_blackjack.deal()
                elif 200 <= mouse_pos[1] <= 250 and play_blackjack.game_state == "playing":
                    play_blackjack.hit()
                elif 300 <= mouse_pos[1] <= 350 and play_blackjack.game_state == "playing":
                    play_blackjack.stand()
                elif 500 <= mouse_pos[1] <= 550:
                    play_blackjack.exit()
    
    # Update animation
    if play_blackjack.flip_animation and play_blackjack.flip_animation.animating:
        play_blackjack.flip_animation.update()
    
    play_blackjack.update_display()
    clock.tick(60)

pygame.quit()
sys.exit()