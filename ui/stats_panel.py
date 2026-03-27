"""
Stats Panel for Neural Flappy Bird.
Displays a generation fitness history line graph.
"""

import pygame
from utils.colors import (
    BG_COLOR, PANEL_BORDER, GRID_LINE,
    GRAPH_LINE, GRAPH_DOT_CURRENT, BEST_EVER_LINE,
    HUD_TEXT, ACCENT,
)
from utils.fonts import get_font


class StatsPanel:
    """Renders a fitness history graph in the bottom-right panel."""

    PANEL_X = 800
    PANEL_Y = 400
    PANEL_W = 400
    PANEL_H = 300

    GRAPH_MARGIN_LEFT = 55
    GRAPH_MARGIN_RIGHT = 20
    GRAPH_MARGIN_TOP = 40
    GRAPH_MARGIN_BOTTOM = 35
    MAX_GENS_DISPLAYED = 50

    def __init__(self):
        pass

    def draw(
        self,
        surface: pygame.Surface,
        fitness_history: list[float],
        best_fitness_ever: float,
    ) -> None:
        """Draw the stats panel with fitness history graph."""
        # Panel background
        panel_rect = pygame.Rect(self.PANEL_X, self.PANEL_Y, self.PANEL_W, self.PANEL_H)
        pygame.draw.rect(surface, BG_COLOR, panel_rect)
        pygame.draw.rect(surface, PANEL_BORDER, panel_rect, 1)

        # Title
        title_font = get_font(12, bold=True)
        title_surf = title_font.render("FITNESS HISTORY", True, HUD_TEXT)
        surface.blit(title_surf, (self.PANEL_X + 15, self.PANEL_Y + 12))

        # Graph area
        gx = self.PANEL_X + self.GRAPH_MARGIN_LEFT
        gy = self.PANEL_Y + self.GRAPH_MARGIN_TOP
        gw = self.PANEL_W - self.GRAPH_MARGIN_LEFT - self.GRAPH_MARGIN_RIGHT
        gh = self.PANEL_H - self.GRAPH_MARGIN_TOP - self.GRAPH_MARGIN_BOTTOM

        # Graph border
        graph_rect = pygame.Rect(gx, gy, gw, gh)
        pygame.draw.rect(surface, PANEL_BORDER, graph_rect, 1)

        if not fitness_history:
            no_data_font = get_font(12)
            no_data = no_data_font.render("Waiting for data...", True, HUD_TEXT)
            surface.blit(no_data, (gx + gw // 2 - no_data.get_width() // 2, gy + gh // 2))
            return

        # Determine display range
        display_data = fitness_history[-self.MAX_GENS_DISPLAYED:]
        start_gen = max(1, len(fitness_history) - self.MAX_GENS_DISPLAYED + 1)
        n = len(display_data)

        # Y-axis scale
        max_fitness = max(max(display_data), best_fitness_ever, 100)
        min_fitness = 0

        # Grid lines (horizontal)
        label_font = get_font(10)
        n_grid_lines = 5
        for i in range(n_grid_lines + 1):
            frac = i / n_grid_lines
            line_y = gy + gh - int(frac * gh)
            pygame.draw.line(surface, GRID_LINE, (gx, line_y), (gx + gw, line_y), 1)
            # Y-axis label
            val = min_fitness + frac * (max_fitness - min_fitness)
            label = label_font.render(f"{int(val)}", True, HUD_TEXT)
            surface.blit(label, (gx - label.get_width() - 6, line_y - label.get_height() // 2))

        # Grid lines (vertical)
        if n > 1:
            v_spacing = max(1, n // 5)
            for i in range(0, n, v_spacing):
                frac = i / max(n - 1, 1)
                line_x = gx + int(frac * gw)
                pygame.draw.line(surface, GRID_LINE, (line_x, gy), (line_x, gy + gh), 1)
                gen_label = label_font.render(f"{start_gen + i}", True, HUD_TEXT)
                surface.blit(gen_label, (line_x - gen_label.get_width() // 2, gy + gh + 5))

        # Best ever horizontal dashed line
        if max_fitness > 0:
            best_y = gy + gh - int((best_fitness_ever / max_fitness) * gh)
            best_y = max(gy, min(gy + gh, best_y))
            dash_len = 8
            gap_len = 6
            x_pos = gx
            while x_pos < gx + gw:
                end_x = min(x_pos + dash_len, gx + gw)
                pygame.draw.line(surface, BEST_EVER_LINE, (x_pos, best_y), (end_x, best_y), 1)
                x_pos += dash_len + gap_len
            best_label = label_font.render(f"best: {int(best_fitness_ever)}", True, BEST_EVER_LINE)
            surface.blit(best_label, (gx + gw - best_label.get_width() - 4, best_y - 16))

        # Plot line
        if n >= 2:
            points = []
            for i, fitness in enumerate(display_data):
                frac_x = i / max(n - 1, 1)
                frac_y = fitness / max_fitness if max_fitness > 0 else 0
                px = gx + int(frac_x * gw)
                py = gy + gh - int(frac_y * gh)
                py = max(gy, min(gy + gh, py))
                points.append((px, py))

            # Line segments
            for i in range(len(points) - 1):
                pygame.draw.line(surface, GRAPH_LINE, points[i], points[i + 1], 2)

            # Dots
            for i, pt in enumerate(points):
                if i == len(points) - 1:
                    # Current generation — highlight
                    pygame.draw.circle(surface, GRAPH_DOT_CURRENT, pt, 5)
                    pygame.draw.circle(surface, (255, 255, 255), pt, 5, 1)
                else:
                    pygame.draw.circle(surface, GRAPH_LINE, pt, 3)
        elif n == 1:
            frac_y = display_data[0] / max_fitness if max_fitness > 0 else 0
            px = gx + gw // 2
            py = gy + gh - int(frac_y * gh)
            py = max(gy, min(gy + gh, py))
            pygame.draw.circle(surface, GRAPH_DOT_CURRENT, (px, py), 5)

        # X axis label
        x_label = label_font.render("Generation", True, HUD_TEXT)
        surface.blit(x_label, (gx + gw // 2 - x_label.get_width() // 2, gy + gh + 18))

        # Y axis label (rotated)
        y_label = label_font.render("Fitness", True, HUD_TEXT)
        y_label_rot = pygame.transform.rotate(y_label, 90)
        surface.blit(y_label_rot, (self.PANEL_X + 6, gy + gh // 2 - y_label_rot.get_height() // 2))
