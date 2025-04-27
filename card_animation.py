import pygame



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
        for i in range(2):  # 
            frame_path = f'Card Flip/{i}.png' 
            img = pygame.image.load(frame_path).convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), 
                                                 int(img.get_height() * scale)))
            self.animation_frames.append(img)
        
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