"""
HUD overlay for Neural Flappy Bird.
Displays generation, alive count, score, best score, species, FPS,
and speed control info on the game panel.
"""

import pygame
from utils.colors import HUD_TEXT, ACCENT
from utils.fonts import get_font


class HUD:
    """Heads-up display overlay on the game panel."""

    def __init__(self):
        self.x = 12
        self.y = 12
        self.line_height = 22
        self.speed_multiplier = 1
        self.paused = False
        self.showcase_mode = False

    def draw(
        self,
        surface: pygame.Surface,
        generation: int,
        alive: int,
        total: int,
        score: int,
        best_score: int,
        species: int,
        fps: float,
    ) -> None:
        """Draw the HUD overlay."""
        font = get_font(14)
        y = self.y

        lines = [
            ("GEN     ", f"{generation:03d}"),
            ("ALIVE   ", f"{alive:3d} / {total}"),
            ("SCORE   ", f"{score}"),
            ("BEST    ", f"{best_score}"),
            ("SPECIES ", f"{species}"),
            ("FPS     ", f"{int(fps)}"),
        ]

        # Semi-transparent background
        bg_height = len(lines) * self.line_height + 16
        bg_width = 200
        bg_surf = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 140))
        surface.blit(bg_surf, (self.x - 4, self.y - 4))

        for label, value in lines:
            label_surf = font.render(label + ": ", True, HUD_TEXT)
            value_surf = font.render(value, True, ACCENT)
            surface.blit(label_surf, (self.x, y))
            surface.blit(value_surf, (self.x + label_surf.get_width(), y))
            y += self.line_height

        # Speed indicator
        speed_text = f"SPEED: {self.speed_multiplier}x"
        if self.paused:
            speed_text = "PAUSED"
        speed_surf = font.render(speed_text, True, ACCENT)
        surface.blit(speed_surf, (self.x, y + 8))

        # Showcase mode banner
        if self.showcase_mode:
            banner_font = get_font(18, bold=True)
            banner_surf = banner_font.render("SHOWCASE MODE", True, ACCENT)
            bx = (800 - banner_surf.get_width()) // 2
            # Background for banner
            banner_bg = pygame.Surface(
                (banner_surf.get_width() + 24, banner_surf.get_height() + 12),
                pygame.SRCALPHA,
            )
            banner_bg.fill((0, 0, 0, 180))
            surface.blit(banner_bg, (bx - 12, 8))
            surface.blit(banner_surf, (bx, 14))

    def draw_controls_hint(self, surface: pygame.Surface) -> None:
        """Draw small controls hint at bottom of game panel."""
        font = get_font(11)
        hints = [
            "SPACE:pause  UP/DOWN:speed  R:restart  S:save  L:load",
        ]
        y = 680
        for hint in hints:
            hint_surf = font.render(hint, True, (80, 80, 80))
            surface.blit(hint_surf, (12, y))
            y += 16
