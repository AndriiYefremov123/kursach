import pygame

screen_width = 1450
screen_height = 950


bg_colour = (53, 101, 77)
black = (0,0,0)
red = (255,0,0)
grey = (220,220,220)
green = (0, 200, 0)

light_slat = (119,136,153)
dark_slat = (47, 79, 79)
dark_red = (255, 0, 0)
pygame.init()
font = pygame.font.SysFont('Verdana', 20)
textfont = pygame.font.SysFont('Verdana', 35)
game_end = pygame.font.SysFont('Verdana', 50)
blackjack = pygame.font.SysFont('Verdana', 70)
SUITS = ['C', 'S', 'H', 'D']

RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
CARD_SIZE = (72, 96)
CARD_CENTER = (36, 48)
CARD_BACK_SIZE = (72, 96)
CARD_BACK_CENTER = (36, 48)
DECK_X = 1100  # X позиція колоди
DECK_Y = 50  # Y позиція колоди
DECK_WIDTH = 100  # ширина
DECK_HEIGHT = 150 # висота