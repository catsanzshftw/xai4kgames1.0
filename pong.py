import pygame
import numpy as np
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle settings
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
PADDLE_SPEED = 5

# Ball settings
BALL_SIZE = 15
BALL_SPEED = 7

# Font for score and game over
font = pygame.font.Font(None, 74)
game_over_font = pygame.font.Font(None, 100)

# Sound generation
def make_beep(frequency=440, duration=0.1, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    stereo_wave = np.stack((wave, wave), axis=1)
    return pygame.sndarray.make_sound((32767 * stereo_wave).astype(np.int16))

beep_paddle = make_beep(440, 0.1)  # Paddle hit sound
boop_wall = make_beep(220, 0.1)   # Wall hit sound
score_sound = make_beep(880, 0.2)  # Score sound

# Game objects
player = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
opponent = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
ball_speed_x = BALL_SPEED
ball_speed_y = BALL_SPEED
player_score = 0
opponent_score = 0
game_over = False

def move_paddle(paddle, up=True):
    if up and paddle.top > 0:
        paddle.y -= PADDLE_SPEED
    if not up and paddle.bottom < HEIGHT:
        paddle.y += PADDLE_SPEED

def move_ball():
    global ball_speed_x, ball_speed_y, player_score, opponent_score, game_over
    if not game_over:
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Wall collision
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_speed_y *= -1
            boop_wall.play()

        # Paddle collision
        if ball.colliderect(player) or ball.colliderect(opponent):
            ball_speed_x *= -1
            beep_paddle.play()

        # Scoring
        if ball.left <= 0:
            opponent_score += 1
            score_sound.play()
            if opponent_score >= 5:
                game_over = True
            else:
                reset_ball()
        if ball.right >= WIDTH:
            player_score += 1
            score_sound.play()
            if player_score >= 5:
                game_over = True
            else:
                reset_ball()

def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_speed_x *= -1
    ball_speed_y *= -1

def simple_ai():
    if not game_over:
        if opponent.centery < ball.centery and opponent.bottom < HEIGHT:
            move_paddle(opponent, False)
        if opponent.centery > ball.centery and opponent.top > 0:
            move_paddle(opponent, True)

def reset_game():
    global player_score, opponent_score, game_over, ball_speed_x, ball_speed_y
    player_score = 0
    opponent_score = 0
    game_over = False
    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_speed_x = BALL_SPEED
    ball_speed_y = BALL_SPEED
    player.center = (50, HEIGHT // 2)
    opponent.center = (WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2)

def setup():
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, player)
    pygame.draw.rect(screen, WHITE, opponent)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
    player_score_text = font.render(str(player_score), True, WHITE)
    opponent_score_text = font.render(str(opponent_score), True, WHITE)
    screen.blit(player_score_text, (WIDTH // 4, 20))
    screen.blit(opponent_score_text, (3 * WIDTH // 4, 20))
    pygame.display.flip()

def update_loop():
    global game_over
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_y:
                reset_game()
            elif event.key == pygame.K_n:
                pygame.quit()
                return

    if not game_over:
        # Player controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            move_paddle(player, True)
        if keys[pygame.K_s]:
            move_paddle(player, False)

        # AI for opponent
        simple_ai()

        # Move ball
        move_ball()

    # Draw everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, player)
    pygame.draw.rect(screen, WHITE, opponent)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
    player_score_text = font.render(str(player_score), True, WHITE)
    opponent_score_text = font.render(str(opponent_score), True, WHITE)
    screen.blit(player_score_text, (WIDTH // 4, 20))
    screen.blit(opponent_score_text, (3 * WIDTH // 4, 20))

    if game_over:
        winner = "Player" if player_score >= 5 else "Opponent"
        game_over_text = game_over_font.render(f"{winner} Wins!", True, WHITE)
        restart_text = font.render("Y: Restart  N: Quit", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()

FPS = 60

async def main():
    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
