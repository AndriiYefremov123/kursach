import pygame
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('BlackJack')

#set framerate
clock = pygame.time.Clock()
FPS = 120

moving_left = False
moving_right = False

#bg colour
BG = (53, 101, 77)
def draw_bg():
    screen.fill(BG)


class Card(pygame.sprite.Sprite):
    def __init__(self, card_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.card_type = card_type
        self.speed = speed
        self.direction = 1
        self.flip = False
        self.animating = False
        self.flipped = False  # Чи перевернута карта
        self.frame_index = 0
        self.animation_delay = 5  # Чим більше число, тим повільніша анімація
        self.animation_counter = 0
        self.animation_list = []

        # Завантаження кадрів анімації перевороту
        for i in range(2):  # Припустимо, що у вас є 10 кадрів анімації
            img = pygame.image.load(f'D:\\study\\інж прог заб\\курсач\\Card Flip\\{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
            self.animation_list.append(img)

        # Завантаження основного зображення карти
        self.front_image = pygame.image.load(f'D:\\study\\інж прог заб\\курсач\\Playing Cards\\card-{self.card_type}.png')
        self.front_image = pygame.transform.scale(self.front_image, (self.front_image.get_width() * scale, self.front_image.get_height() * scale))

        self.back_image = self.animation_list[-1]  # Останній кадр анімації — це зворот карти
        self.image = self.front_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
            
        self.rect.x += dx
        self.rect.y += dy

    def start_flip_animation(self):
        if not self.animating:
            self.animating = True
            self.frame_index = 0
            self.animation_counter = 0

    def update_animation(self):
        if self.animating:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_delay:
                self.animation_counter = 0

                if not self.flipped:
                    if self.frame_index < len(self.animation_list):
                        self.image = self.animation_list[self.frame_index]
                        self.frame_index += 1
                    else:
                        self.animating = False
                        self.flipped = True
                        self.image = self.back_image
                else:
                    if self.frame_index > 0:
                        self.frame_index -= 1
                        self.image = self.animation_list[self.frame_index]
                    else:
                        self.animating = False
                        self.flipped = False
                        self.image = self.front_image

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


playing_card = Card('clubs-1', 100, 300, 1, 1)
playing_card2 = Card('clubs-1', 200, 500, 1, 2)

deck = [playing_card, playing_card2]

run = True
while run:
    clock.tick(FPS)

    draw_bg()

    for card in deck:
        card.update_animation()  # Оновлюємо анімацію
        card.draw()
        card.move(moving_left, moving_right)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:  # Натискання пробілу перевертає карти
                for card in deck:
                    card.start_flip_animation()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
    
    pygame.display.update()

pygame.quit()
