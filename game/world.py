"""
Game world state for Neural Flappy Bird.
Manages birds, pipes, ground, collisions, and scoring.
"""

import pygame
from game.bird import Bird
from game.pipe import PipeManager
from game.ground import Ground


class World:
    """The complete game world for one generation."""

    GAME_WIDTH = 800
    WINDOW_HEIGHT = 700
    BIRD_START_X = 120

    def __init__(self):
        self.pipe_manager = PipeManager()
        self.ground = Ground(self.GAME_WIDTH, self.WINDOW_HEIGHT)
        self.birds: list[Bird] = []
        self.score = 0
        self.best_score = 0
        self.frame_count = 0

    def reset(self, birds: list[Bird]) -> None:
        """Reset world for a new generation with new birds."""
        self.birds = birds
        self.pipe_manager.reset()
        self.score = 0
        self.frame_count = 0

    def get_alive_birds(self) -> list[Bird]:
        """Return list of alive birds."""
        return [b for b in self.birds if b.alive]

    def get_best_bird(self) -> Bird | None:
        """Return the alive bird with the highest current score."""
        alive = self.get_alive_birds()
        if not alive:
            return None
        return max(alive, key=lambda b: b.get_fitness())

    def get_inputs_for_bird(self, bird: Bird) -> list[float]:
        """Calculate normalized neural network inputs for a bird."""
        next_pipe = self.pipe_manager.get_next_pipe(bird.x)

        if next_pipe is None:
            # No pipe ahead — provide default values
            return [
                bird.y / self.WINDOW_HEIGHT,
                bird.velocity / 10.0,
                1.0,  # max distance
                0.5,  # middle of screen
                0.5,
            ]

        pipe_top_y = next_pipe.gap_y - next_pipe.gap_size // 2
        pipe_bot_y = next_pipe.gap_y + next_pipe.gap_size // 2
        dist_to_pipe = next_pipe.x - bird.x

        return [
            bird.y / self.WINDOW_HEIGHT,
            bird.velocity / 10.0,
            dist_to_pipe / self.GAME_WIDTH,
            pipe_top_y / self.WINDOW_HEIGHT,
            pipe_bot_y / self.WINDOW_HEIGHT,
        ]

    def update(self) -> bool:
        """
        Update one frame of the game world.
        Returns True if at least one bird is still alive.
        """
        alive_birds = self.get_alive_birds()
        if not alive_birds:
            return False

        self.frame_count += 1

        # Update pipes
        self.pipe_manager.update(self.GAME_WIDTH)

        # Update ground scroll
        self.ground.update(self.pipe_manager.current_speed)

        # Bird thinking and movement
        for bird in alive_birds:
            inputs = self.get_inputs_for_bird(bird)
            if bird.think(inputs):
                bird.flap()
            bird.update(self.WINDOW_HEIGHT)

        # Check pipe collisions
        alive_birds = self.get_alive_birds()  # refresh after physics
        for bird in alive_birds:
            for pipe in self.pipe_manager.pipes:
                if pipe.collides_with(bird.rect):
                    bird.alive = False

        # Score pipes
        for pipe in self.pipe_manager.pipes:
            if not pipe.scored:
                # Check if any bird has passed this pipe
                alive_birds = self.get_alive_birds()
                if alive_birds and alive_birds[0].x > pipe.x + pipe.WIDTH:
                    pipe.scored = True
                    self.score += 1
                    for bird in alive_birds:
                        bird.pipes_passed += 1

        # Update best score
        if self.score > self.best_score:
            self.best_score = self.score

        # Write fitness to genomes
        for bird in self.birds:
            bird.genome.fitness = bird.get_fitness()

        return len(self.get_alive_birds()) > 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the entire game world onto the surface."""
        # Clip to game panel
        clip_rect = pygame.Rect(0, 0, self.GAME_WIDTH, self.WINDOW_HEIGHT)
        surface.set_clip(clip_rect)

        # Draw pipes
        self.pipe_manager.draw(surface)

        # Draw birds
        for bird in self.birds:
            bird.draw(surface)

        # Draw ground
        self.ground.draw(surface)

        surface.set_clip(None)
