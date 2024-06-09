
import pygame
import random
import time
from pygame.locals import *

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15
GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100
PIPE_WIDTH = 80
PIPE_HEIGHT = 500
PIPE_GAP = 150
WING_SOUND = 'assets/audio/wing.wav'
HIT_SOUND = 'assets/audio/hit.wav'

pygame.mixer.init()

def show_start_screen(screen):
    background = pygame.image.load('assets/sprites/background-day.png')
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    begin_image = pygame.image.load('assets/sprites/message.png').convert_alpha()

    bird_group = pygame.sprite.Group()
    bird = Bird()
    bird_group.add(bird)
    ground_group = pygame.sprite.Group()
    for i in range(2):
        ground = Ground(GROUND_WIDTH * i)
        ground_group.add(ground)

    clock = pygame.time.Clock()

    while True:
        clock.tick(15)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN or event.key == K_SPACE:
                    bird.bump()
                    pygame.mixer.music.load(WING_SOUND)
                    pygame.mixer.music.play()
                    return

        screen.blit(background, (0, 0))
        screen.blit(begin_image, (100, 150))

        if is_off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0])
            new_ground = Ground(GROUND_WIDTH - 20)
            ground_group.add(new_ground)

        bird.begin()
        ground_group.update()

        bird_group.draw(screen)
        ground_group.draw(screen)

        pygame.display.update()


        
def update_high_score(current_score):
    high_score_file = "highscore.txt"

    # Read the previous high score from the file
    try:
        with open(high_score_file, "r") as file:
            high_score = int(file.read())
    except FileNotFoundError:
        high_score = 0

    # Update the high score if necessary
    if current_score > high_score:
        high_score = current_score
        with open(high_score_file, "w") as file:
            file.write(str(high_score))

    return high_score

def show_text(screen, text, position, font_size=30, color=(255, 255, 255)):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = [
            pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()
        ]
        self.speed = SPEED
        self.current_image = 0
        self.image = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDTH / 6
        self.rect[1] = SCREEN_HEIGHT / 3

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]

class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize):
        super().__init__()
        self.image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, PIPE_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.passed = False

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = -(self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)
        self.inverted = inverted

    def update(self):
        self.rect[0] -= GAME_SPEED

class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos):
        super().__init__()
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        self.rect[0] -= GAME_SPEED


def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])


def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted

def pause_game(screen):
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_p:
                    paused = False
                if event.key == K_RETURN or event.key == K_SPACE:
                    cheat_code = input("Enter cheat code: ")
                    apply_cheat_code(cheat_code)
                    paused = False

        # You can display a pause message on the screen if you want:
        show_text(screen, "Paused", (SCREEN_WIDTH / 2.5, SCREEN_HEIGHT / 3), font_size=40, color=(255, 255, 255))
        pygame.display.update()
        

def game():
    global invincible
    invincible = False
    score = 0
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Flappy Bird')

    background = pygame.image.load('assets/sprites/background-day.png')
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    bird_group = pygame.sprite.Group()
    bird = Bird()
    bird_group.add(bird)

    ground_group = pygame.sprite.Group()
    for i in range(2):
        ground = Ground(GROUND_WIDTH * i)
        ground_group.add(ground)

    pipe_group = pygame.sprite.Group()
    for i in range(2):
        pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

    clock = pygame.time.Clock()
    game_over = False
    paused = False
    cheat_code = ""

    while True:
        clock.tick(15)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE or event.key == K_UP:
                    bird.bump()
                    pygame.mixer.music.load(WING_SOUND)
                    pygame.mixer.music.play()
                if event.key == K_p:
                    pause_game(screen)

                if paused:  # Handle text input for cheat codes when paused
                    if event.key == K_BACKSPACE:
                        cheat_code = cheat_code[:-1]
                    else:
                        cheat_code += event.unicode
                    if cheat_code == "INVINCIBLE":
                        invincible = True

        if paused:
            screen.blit(background,xddsafddddssd(0, 0))
            bird_group.draw(screen)
            pipe_group.draw(screen)
            ground_group.draw(screen)
            show_text(screen, f"Score: {score}", (20, 20))
            show_text(screen, "Paused", (SCREEN_WIDTH / 2.5, SCREEN_HEIGHT / 3), font_size=40, color=(255, 0, 0))
            show_text(screen, "Enter cheat code:", (SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2.5), font_size=20)
            show_text(screen, cheat_code, (SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2), font_size=20)
            pygame.display.update()
            continue

        screen.blit(background, (0, 0))

        if is_off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0])

            new_ground = Ground(GROUND_WIDTH - 20)
            ground_group.add(new_ground)

        if is_off_screen(pipe_group.sprites()[0]):
            pipe_group.remove(pipe_group.sprites()[0])
            pipe_group.remove(pipe_group.sprites()[0])

            pipes = get_random_pipes(SCREEN_WIDTH * 2)

            pipe_group.add(pipes[0])
            pipe_group.add(pipes[1])

        bird_group.update()
        ground_group.update()
        pipe_group.update()

        for pipe in pipe_group.sprites():
            if pipe.rect[0] + PIPE_WIDTH < bird.rect[0] and not pipe.passed:
                pipe.passed = True
                score += 1

        bird_group.draw(screen)
        pipe_group.draw(screen)
        ground_group.draw(screen)

        show_text(screen, f"Score: {score}", (20, 20))

        pygame.display.update()

        if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
                pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
            if not invincible:  # Add invincibility check here
                pygame.mixer.music.load(HIT_SOUND)
                pygame.mixer.music.play()
                time.sleep(1)
                high_score = update_high_score(score)
                game_over = True
                break

    while game_over:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN or event.key == K_SPACE:
                    game_over = False
                    break

        if not game_over:
            break

        screen.blit(background, (0, 0))
        ground_group.draw(screen)
        bird_group.draw(screen)
        show_text(screen, f"Score: {score}", (20, 20))
        show_text(screen, f"High Score: {high_score}", (20, 50))
        show_text(screen, "Game Over", (SCREEN_WIDTH / 3, SCREEN_HEIGHT / 3), font_size=40, color=(255, 0, 0))
        show_text(screen, "Press Enter/Space to restart", (SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2.5), font_size=20)
        pygame.display.update()

        
def apply_cheat_code(cheat_code):
    global invincible
    if cheat_code == "superbird":
        invincible = True
    elif cheat_code == "extrapoints":
        # Apply "extrapoints" cheat, e.g., increase the score
        pass
    # Add other cheat codes here
    else:
        print("Unknown cheat code:", cheat_code)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Flappy Bird')
    game_over = False
    while not game_over:
        show_start_screen(screen)
        game()
        for event in pygame.event.get():
            if event.type == QUIT:
                game_over = True
            if event.type == KEYDOWN:
                if event.key == K_RETURN or event.key == K_SPACE:
                    game_over = False



