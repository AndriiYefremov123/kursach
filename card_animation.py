import pygame


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


        for i in range(2):  # Два кадри анімації (задня і передня сторона)
            img = pygame.image.load(f'Card Flip/{i}.png').convert()
            img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
            self.animation_list.append(img)
        self.front_image = pygame.image.load('img/back.png')
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
                        self.image = self.front_image
    def draw(self, surface):
        # Якщо анімація триває, відображаємо поточний кадр
        if self.animating:
            surface.blit(self.image, (self.x, self.y))  # Показуємо поточний кадр анімації
        else:
            surface.blit(self.front_image, (self.x, self.y))  # Після анімації показуємо передню сторону карти
