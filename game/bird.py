"""
Bird entity for Neural Flappy Bird.
Handles physics, animation, rendering, and genome binding.
"""

import math
import pygame
from utils.colors import SPECIES_COLORS, WHITE


class Bird:
    """A single bird controlled by a NEAT neural network."""

    GRAVITY = 0.5
    FLAP_VELOCITY = -8.0
    MAX_FALL_VELOCITY = 10.0
    WIDTH = 30
    HEIGHT = 22

    def __init__(self, x: float, y: float, genome, network, species_id: int = 0):
        self.x = x
        self.y = y
        self.velocity = 0.0
        self.genome = genome
        self.network = network
        self.alive = True
        self.score = 0
        self.pipes_passed = 0
        self.frames_alive = 0
        self.ceiling_hits = 0

        # Visual
        self.species_id = species_id
        self.color = SPECIES_COLORS[species_id % len(SPECIES_COLORS)]
        self.rotation = 0.0  # degrees
        self.flap_timer = 0  # frames since last flap for wing animation

        # Collision rect with inset margin
        self._update_rect()

    def _update_rect(self) -> None:
        """Update the collision rect (6px inset margin)."""
        margin = 6
        self.rect = pygame.Rect(
            self.x - self.WIDTH // 2 + margin,
            self.y - self.HEIGHT // 2 + margin,
            self.WIDTH - margin * 2,
            self.HEIGHT - margin * 2,
        )

    def flap(self) -> None:
        """Apply upward flap velocity."""
        self.velocity = self.FLAP_VELOCITY
        self.rotation = 25.0
        self.flap_timer = 8

    def update(self, window_height: int) -> None:
        """Update bird physics for one frame."""
        if not self.alive:
            return

        # Gravity
        self.velocity += self.GRAVITY
        if self.velocity > self.MAX_FALL_VELOCITY:
            self.velocity = self.MAX_FALL_VELOCITY

        self.y += self.velocity

        # Rotation animation
        if self.velocity < 0:
            self.rotation = min(25.0, self.rotation + 3)
        else:
            self.rotation = max(-90.0, self.rotation - 2.5)

        # Wing flap timer
        if self.flap_timer > 0:
            self.flap_timer -= 1

        # Ceiling collision
        if self.y < self.HEIGHT // 2:
            self.y = self.HEIGHT // 2
            self.velocity = 0
            self.ceiling_hits += 1

        # Floor collision (ground at window_height - 60)
        ground_y = window_height - 60
        if self.y > ground_y - self.HEIGHT // 2:
            self.alive = False

        self.frames_alive += 1
        self._update_rect()

    def think(self, inputs: list[float]) -> bool:
        """Feed inputs to the neural network and decide to flap."""
        output = self.network.activate(inputs)
        return output[0] > 0.5

    def get_fitness(self) -> float:
        """Calculate current fitness score."""
        fitness = self.frames_alive * 0.1 + self.pipes_passed * 50.0
        # Penalize ceiling hugging
        if self.ceiling_hits > 5:
            fitness -= (self.ceiling_hits - 5) * 10.0
        return max(0.0, fitness)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the bird as a rounded polygon (no sprites)."""
        if not self.alive:
            return

        # Create bird surface for rotation
        bird_surf = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

        # Body — rounded rectangle
        body_rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        pygame.draw.rect(bird_surf, self.color, body_rect, border_radius=8)

        # Eye
        eye_x = self.WIDTH - 9
        eye_y = 7
        pygame.draw.circle(bird_surf, WHITE, (eye_x, eye_y), 4)
        pygame.draw.circle(bird_surf, (20, 20, 20), (eye_x + 1, eye_y), 2)

        # Beak
        beak_color = (255, 200, 60)
        beak_points = [
            (self.WIDTH - 2, self.HEIGHT // 2 - 2),
            (self.WIDTH + 6, self.HEIGHT // 2),
            (self.WIDTH - 2, self.HEIGHT // 2 + 2),
        ]
        pygame.draw.polygon(bird_surf, beak_color, beak_points)

        # Wing animation
        wing_color = tuple(max(0, c - 40) for c in self.color)
        if self.flap_timer > 4:
            # Wing up
            wing_points = [(6, 8), (14, 2), (18, 10)]
        elif self.flap_timer > 0:
            # Wing mid
            wing_points = [(6, 10), (14, 8), (18, 12)]
        else:
            # Wing down
            wing_points = [(6, 12), (14, 14), (18, 12)]
        pygame.draw.polygon(bird_surf, wing_color, wing_points)

        # Rotate
        rotated = pygame.transform.rotate(bird_surf, self.rotation)
        rotated_rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rotated_rect.topleft)
