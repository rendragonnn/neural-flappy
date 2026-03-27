"""
Pipe system for Neural Flappy Bird.
Handles pipe generation, scrolling, gap logic, and rendering.
"""

import random
import pygame
from utils.colors import PIPE_COLOR, PIPE_CAP_COLOR


class Pipe:
    """A single pipe pair (top and bottom) with a gap."""

    WIDTH = 70
    CAP_HEIGHT = 26
    CAP_OVERHANG = 6  # extra width on each side for the cap

    def __init__(self, x: float, gap_y: float, gap_size: int = 160, speed: float = 4.0):
        self.x = x
        self.gap_y = gap_y
        self.gap_size = gap_size
        self.speed = speed
        self.scored = False  # whether birds have been scored for passing this pipe

        # Rects
        self._update_rects()

    def _update_rects(self) -> None:
        """Update collision and rendering rects."""
        top_h = self.gap_y - self.gap_size // 2
        bottom_top = self.gap_y + self.gap_size // 2

        self.top_rect = pygame.Rect(int(self.x), 0, self.WIDTH, max(0, int(top_h)))
        self.bottom_rect = pygame.Rect(
            int(self.x), int(bottom_top), self.WIDTH, 700 - int(bottom_top)
        )

        # Cap rects
        self.top_cap_rect = pygame.Rect(
            int(self.x) - self.CAP_OVERHANG,
            max(0, int(top_h) - self.CAP_HEIGHT),
            self.WIDTH + self.CAP_OVERHANG * 2,
            self.CAP_HEIGHT,
        )
        self.bottom_cap_rect = pygame.Rect(
            int(self.x) - self.CAP_OVERHANG,
            int(bottom_top),
            self.WIDTH + self.CAP_OVERHANG * 2,
            self.CAP_HEIGHT,
        )

    def update(self) -> None:
        """Move pipe to the left."""
        self.x -= self.speed
        self._update_rects()

    def is_off_screen(self) -> bool:
        """Check if pipe has scrolled fully off screen."""
        return self.x + self.WIDTH < -10

    def collides_with(self, bird_rect: pygame.Rect) -> bool:
        """Check if a bird rect collides with this pipe pair."""
        return self.top_rect.colliderect(bird_rect) or self.bottom_rect.colliderect(bird_rect)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the pipe pair with caps."""
        # Top pipe body
        if self.top_rect.height > 0:
            pygame.draw.rect(surface, PIPE_COLOR, self.top_rect, border_radius=4)
        # Top pipe cap
        if self.top_rect.height > 0:
            pygame.draw.rect(surface, PIPE_CAP_COLOR, self.top_cap_rect, border_radius=6)

        # Bottom pipe body
        pygame.draw.rect(surface, PIPE_COLOR, self.bottom_rect, border_radius=4)
        # Bottom pipe cap
        pygame.draw.rect(surface, PIPE_CAP_COLOR, self.bottom_cap_rect, border_radius=6)


class PipeManager:
    """Manages the spawning and lifecycle of pipes."""

    SPAWN_INTERVAL = 380  # frames between pipes
    GAP_MIN_Y = 150
    GAP_MAX_Y = 500
    BASE_SPEED = 4.0
    SPEED_INCREMENT = 0.1  # per 5 pipes

    def __init__(self):
        self.pipes: list[Pipe] = []
        self.frame_counter = 0
        self.total_pipes_spawned = 0
        self.current_speed = self.BASE_SPEED

    def reset(self) -> None:
        """Reset pipe manager for a new generation."""
        self.pipes.clear()
        self.frame_counter = 0
        self.total_pipes_spawned = 0
        self.current_speed = self.BASE_SPEED

    def update(self, game_width: int) -> None:
        """Update all pipes and spawn new ones as needed."""
        self.frame_counter += 1

        # Spawn new pipe
        if self.frame_counter >= self.SPAWN_INTERVAL:
            self.frame_counter = 0
            gap_y = random.randint(self.GAP_MIN_Y, self.GAP_MAX_Y)
            pipe = Pipe(game_width + 10, gap_y, speed=self.current_speed)
            self.pipes.append(pipe)
            self.total_pipes_spawned += 1

            # Increase speed every 5 pipes
            if self.total_pipes_spawned % 5 == 0:
                self.current_speed += self.SPEED_INCREMENT

        # Update existing pipes
        for pipe in self.pipes:
            pipe.speed = self.current_speed
            pipe.update()

        # Remove off-screen pipes
        self.pipes = [p for p in self.pipes if not p.is_off_screen()]

    def get_next_pipe(self, bird_x: float) -> Pipe | None:
        """Get the next pipe ahead of the bird's x position."""
        for pipe in self.pipes:
            if pipe.x + pipe.WIDTH > bird_x:
                return pipe
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all pipes."""
        for pipe in self.pipes:
            pipe.draw(surface)
