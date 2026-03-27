"""
Real-time Neural Network Visualizer for Neural Flappy Bird.
Displays the best bird's network with input/hidden/output nodes,
weighted connections, and activation pulse animations.
"""

import math
import pygame
import neat
from utils.colors import (
    NODE_INPUT, NODE_HIDDEN, NODE_OUTPUT,
    WEIGHT_POSITIVE, WEIGHT_NEGATIVE, NODE_PULSE_WHITE,
    PANEL_BORDER, HUD_TEXT, ACCENT, BG_COLOR,
)
from utils.fonts import get_font


class NeuralNetVisualizer:
    """Draws a real-time neural network graph on the right panel."""

    PANEL_X = 800
    PANEL_Y = 0
    PANEL_W = 400
    PANEL_H = 400

    INPUT_LABELS = ["bird_y", "velocity", "dist", "pipe_top", "pipe_bot"]
    OUTPUT_LABELS = ["FLAP"]

    NODE_RADIUS = 14
    LABEL_FONT_SIZE = 11
    VALUE_FONT_SIZE = 10

    def __init__(self):
        self.dash_offset = 0.0  # for animated dash flow

    def draw(
        self,
        surface: pygame.Surface,
        genome: neat.DefaultGenome | None,
        config: neat.Config | None,
        net: object | None,
        node_values: dict[int, float] | None,
        generation: int = 0,
        species_id: int = 0,
    ) -> None:
        """Draw the neural network visualization panel."""
        # Panel background
        panel_rect = pygame.Rect(self.PANEL_X, self.PANEL_Y, self.PANEL_W, self.PANEL_H)
        pygame.draw.rect(surface, BG_COLOR, panel_rect)
        pygame.draw.rect(surface, PANEL_BORDER, panel_rect, 1)

        # Header
        header_font = get_font(13, bold=True)
        header_text = f"Gen {generation} — Species {species_id}"
        header_surf = header_font.render(header_text, True, ACCENT)
        surface.blit(header_surf, (self.PANEL_X + 15, self.PANEL_Y + 12))

        title_font = get_font(11)
        title_surf = title_font.render("NEURAL NETWORK", True, HUD_TEXT)
        surface.blit(title_surf, (self.PANEL_X + self.PANEL_W - title_surf.get_width() - 15, self.PANEL_Y + 14))

        if genome is None or config is None:
            msg_font = get_font(14)
            msg = msg_font.render("No bird active", True, HUD_TEXT)
            surface.blit(msg, (self.PANEL_X + self.PANEL_W // 2 - msg.get_width() // 2, 200))
            return

        # Resolve node values if not provided
        if node_values is None:
            node_values = {}

        # Gather node info
        input_keys = sorted(config.genome_config.input_keys)
        output_keys = sorted(config.genome_config.output_keys)
        hidden_keys = sorted(
            k for k in genome.nodes.keys()
            if k not in input_keys and k not in output_keys
        )

        # Position nodes
        margin_x = 70
        margin_y = 60
        usable_w = self.PANEL_W - margin_x * 2
        usable_h = self.PANEL_H - margin_y * 2 - 20

        node_positions: dict[int, tuple[int, int]] = {}

        # Input nodes — left column
        n_inputs = len(input_keys)
        for i, key in enumerate(input_keys):
            x = self.PANEL_X + margin_x
            y = self.PANEL_Y + margin_y + 20 + int(i * usable_h / max(n_inputs - 1, 1))
            node_positions[key] = (x, y)

        # Output nodes — right column
        n_outputs = len(output_keys)
        for i, key in enumerate(output_keys):
            x = self.PANEL_X + self.PANEL_W - margin_x
            y = self.PANEL_Y + margin_y + 20 + int(usable_h / 2)
            node_positions[key] = (x, y)

        # Hidden nodes — middle, spread vertically
        if hidden_keys:
            n_hidden = len(hidden_keys)
            mid_x = self.PANEL_X + self.PANEL_W // 2
            for i, key in enumerate(hidden_keys):
                y = self.PANEL_Y + margin_y + 20 + int(i * usable_h / max(n_hidden - 1, 1))
                node_positions[key] = (mid_x, y)

        # Draw connections
        self.dash_offset += 0.5
        if self.dash_offset > 20:
            self.dash_offset = 0

        for cg in genome.connections.values():
            if cg.key[0] not in node_positions or cg.key[1] not in node_positions:
                continue

            start = node_positions[cg.key[0]]
            end = node_positions[cg.key[1]]
            weight = cg.weight
            enabled = cg.enabled

            # Color based on weight sign
            if weight >= 0:
                color = WEIGHT_POSITIVE
            else:
                color = WEIGHT_NEGATIVE

            # Thickness from weight magnitude
            thickness = max(1, min(4, int(abs(weight) * 1.5)))

            # Opacity
            if not enabled:
                alpha = 50
            else:
                # Check if input node is active
                input_val = abs(node_values.get(cg.key[0], 0))
                alpha = max(60, min(255, int(60 + input_val * 195)))

            # Draw connection line with alpha
            conn_surf = pygame.Surface((self.PANEL_W, self.PANEL_H), pygame.SRCALPHA)
            adjusted_start = (start[0] - self.PANEL_X, start[1] - self.PANEL_Y)
            adjusted_end = (end[0] - self.PANEL_X, end[1] - self.PANEL_Y)
            line_color = (*color, alpha)
            pygame.draw.line(conn_surf, line_color, adjusted_start, adjusted_end, thickness)

            # Animated dash marks for active connections
            if enabled and alpha > 100:
                dx = adjusted_end[0] - adjusted_start[0]
                dy = adjusted_end[1] - adjusted_start[1]
                length = math.sqrt(dx * dx + dy * dy)
                if length > 0:
                    nx, ny = dx / length, dy / length
                    dash_spacing = 20
                    offset = self.dash_offset
                    while offset < length:
                        px = adjusted_start[0] + nx * offset
                        py = adjusted_start[1] + ny * offset
                        pygame.draw.circle(
                            conn_surf,
                            (*ACCENT, min(255, alpha + 40)),
                            (int(px), int(py)),
                            2,
                        )
                        offset += dash_spacing

            surface.blit(conn_surf, (self.PANEL_X, self.PANEL_Y))

        # Draw nodes
        label_font = get_font(self.LABEL_FONT_SIZE)
        value_font = get_font(self.VALUE_FONT_SIZE)

        for key, pos in node_positions.items():
            # Determine node color
            if key in input_keys:
                color = NODE_INPUT
            elif key in output_keys:
                color = NODE_OUTPUT
            else:
                color = NODE_HIDDEN

            val = node_values.get(key, 0.0)

            # Node circle
            pygame.draw.circle(surface, color, pos, self.NODE_RADIUS)
            pygame.draw.circle(surface, (40, 40, 40), pos, self.NODE_RADIUS, 1)

            # Pulse animation when firing (value > 0.5)
            if abs(val) > 0.5:
                pulse_radius = self.NODE_RADIUS + 4 + int(2 * math.sin(pygame.time.get_ticks() * 0.01))
                pulse_surf = pygame.Surface(
                    (pulse_radius * 2 + 4, pulse_radius * 2 + 4), pygame.SRCALPHA
                )
                pygame.draw.circle(
                    pulse_surf,
                    (*NODE_PULSE_WHITE, 100),
                    (pulse_radius + 2, pulse_radius + 2),
                    pulse_radius,
                    2,
                )
                surface.blit(
                    pulse_surf,
                    (pos[0] - pulse_radius - 2, pos[1] - pulse_radius - 2),
                )

            # Node value text
            val_text = f"{val:.2f}"
            val_surf = value_font.render(val_text, True, (220, 220, 220))
            surface.blit(
                val_surf,
                (pos[0] - val_surf.get_width() // 2, pos[1] - val_surf.get_height() // 2),
            )

            # Labels
            if key in input_keys:
                idx = input_keys.index(key)
                label = self.INPUT_LABELS[idx] if idx < len(self.INPUT_LABELS) else f"in_{idx}"
                label_surf = label_font.render(label, True, HUD_TEXT)
                surface.blit(label_surf, (pos[0] - self.NODE_RADIUS - label_surf.get_width() - 8, pos[1] - label_surf.get_height() // 2))
            elif key in output_keys:
                idx = output_keys.index(key)
                label = self.OUTPUT_LABELS[idx] if idx < len(self.OUTPUT_LABELS) else f"out_{idx}"
                label_surf = label_font.render(label, True, HUD_TEXT)
                surface.blit(label_surf, (pos[0] + self.NODE_RADIUS + 8, pos[1] - label_surf.get_height() // 2))
