import random
import sys
from dataclasses import dataclass

import pygame


SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

BIRD_SIZE = 28
BIRD_X = 80
GRAVITY = 0.35
FLAP_STRENGTH = -7.5

PIPE_WIDTH = 70
PIPE_GAP = 150
PIPE_SPEED = 3.2
PIPE_SPAWN_MS = 1400

GROUND_HEIGHT = 80

SKY_COLOR = (135, 206, 235)
BIRD_COLOR = (255, 215, 0)
PIPE_COLOR = (34, 139, 34)
GROUND_COLOR = (222, 184, 135)
TEXT_COLOR = (35, 35, 35)


@dataclass
class Bird:
    x: int
    y: float
    velocity: float

    def flap(self) -> None:
        self.velocity = FLAP_STRENGTH

    def update(self) -> None:
        self.velocity += GRAVITY
        self.y += self.velocity

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, int(self.y), BIRD_SIZE, BIRD_SIZE)


@dataclass
class PipePair:
    x: float
    gap_y: int
    passed: bool = False

    def update(self) -> None:
        self.x -= PIPE_SPEED

    def top_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), 0, PIPE_WIDTH, self.gap_y)

    def bottom_rect(self) -> pygame.Rect:
        bottom_height = SCREEN_HEIGHT - GROUND_HEIGHT - (self.gap_y + PIPE_GAP)
        return pygame.Rect(
            int(self.x),
            self.gap_y + PIPE_GAP,
            PIPE_WIDTH,
            bottom_height,
        )

    def offscreen(self) -> bool:
        return self.x + PIPE_WIDTH < 0


class Game:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 28, bold=True)
        self.big_font = pygame.font.SysFont("arial", 36, bold=True)
        self.reset()

    def reset(self) -> None:
        self.bird = Bird(BIRD_X, SCREEN_HEIGHT // 2, 0)
        self.pipes: list[PipePair] = []
        self.score = 0
        self.game_over = False
        self.next_pipe_time = pygame.time.get_ticks() + PIPE_SPAWN_MS

    def spawn_pipe(self) -> None:
        gap_y = random.randint(120, SCREEN_HEIGHT - GROUND_HEIGHT - PIPE_GAP - 120)
        self.pipes.append(PipePair(SCREEN_WIDTH + 20, gap_y))

    def handle_input(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if not self.game_over:
                        self.bird.flap()
                    else:
                        self.reset()
                if event.key == pygame.K_r and self.game_over:
                    self.reset()

    def update(self) -> None:
        if self.game_over:
            return

        now = pygame.time.get_ticks()
        if now >= self.next_pipe_time:
            self.spawn_pipe()
            self.next_pipe_time = now + PIPE_SPAWN_MS

        self.bird.update()
        for pipe in self.pipes:
            pipe.update()

        self.pipes = [pipe for pipe in self.pipes if not pipe.offscreen()]

        bird_rect = self.bird.rect()
        if bird_rect.top <= 0 or bird_rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
            self.game_over = True

        for pipe in self.pipes:
            if bird_rect.colliderect(pipe.top_rect()) or bird_rect.colliderect(
                pipe.bottom_rect()
            ):
                self.game_over = True
            if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.passed = True
                self.score += 1

    def draw_background(self) -> None:
        self.screen.fill(SKY_COLOR)
        ground_rect = pygame.Rect(0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)
        pygame.draw.rect(self.screen, GROUND_COLOR, ground_rect)

    def draw_pipes(self) -> None:
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, PIPE_COLOR, pipe.top_rect())
            pygame.draw.rect(self.screen, PIPE_COLOR, pipe.bottom_rect())

    def draw_bird(self) -> None:
        pygame.draw.rect(self.screen, BIRD_COLOR, self.bird.rect(), border_radius=6)

    def draw_score(self) -> None:
        score_surface = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_surface, (20, 20))

    def draw_game_over(self) -> None:
        if not self.game_over:
            return
        title = self.big_font.render("Game Over", True, TEXT_COLOR)
        subtitle = self.font.render("Press Space or R to restart", True, TEXT_COLOR)
        self.screen.blit(
            title,
            (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 60),
        )
        self.screen.blit(
            subtitle,
            (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 2 - 10),
        )

    def run(self) -> None:
        while True:
            self.handle_input()
            self.update()
            self.draw_background()
            self.draw_pipes()
            self.draw_bird()
            self.draw_score()
            self.draw_game_over()
            pygame.display.flip()
            self.clock.tick(FPS)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Flappy Bird")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = Game(screen)
    game.run()


if __name__ == "__main__":
    main()
