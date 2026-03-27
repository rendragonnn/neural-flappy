"""
Scrolling ground for Neural Flappy Bird.
"""

import pygame
from utils.colors import GROUND_COLOR, GROUND_STRIPE


class Ground:
    """Scrolling ground at the bottom of the game panel."""

    HEIGHT = 60
    STRIPE_HEIGHT = 4

    def __init__(self, width: int, window_height: int):
        self.width = width
        self.window_height = window_height
        self.y = window_height - self.HEIGHT
        self.scroll_x = 0.0
        self.tile_width = 40  # width of each ground segment for scrolling pattern

    def update(self, speed: float) -> None:
        """Scroll ground to the left."""
        self.scroll_x -= speed
        if abs(self.scroll_x) >= self.tile_width:
            self.scroll_x = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the scrolling ground with stripe pattern."""
        # Main ground fill
        ground_rect = pygame.Rect(0, self.y, self.width, self.HEIGHT)
        pygame.draw.rect(surface, GROUND_COLOR, ground_rect)

        # Top stripe
        stripe_rect = pygame.Rect(0, self.y, self.width, self.STRIPE_HEIGHT)
        pygame.draw.rect(surface, GROUND_STRIPE, stripe_rect)

        # Scrolling dash pattern on the stripe
        dash_width = 20
        gap_width = 20
        total = dash_width + gap_width
        x = int(self.scroll_x) % total - total
        while x < self.width:
            dash_rect = pygame.Rect(x, self.y + self.STRIPE_HEIGHT, dash_width, 2)
            pygame.draw.rect(surface, GROUND_STRIPE, dash_rect)
            x += total

    def get_top_y(self) -> int:
        """Return the y coordinate of the ground surface."""
        return self.y
