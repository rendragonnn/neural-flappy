"""
Color constants for Neural Flappy Bird.
All colors are RGB tuples for Pygame.
"""

# Background & panels
BG_COLOR = (13, 13, 13)            # #0D0D0D
PANEL_DIVIDER = (30, 30, 30)       # #1E1E1E
PANEL_BORDER = (42, 42, 42)        # #2A2A2A

# Ground
GROUND_COLOR = (26, 26, 26)        # #1A1A1A
GROUND_STRIPE = (44, 44, 44)       # #2C2C2C

# Pipes
PIPE_COLOR = (27, 58, 45)          # #1B3A2D
PIPE_CAP_COLOR = (15, 42, 30)      # #0F2A1E

# HUD
HUD_TEXT = (192, 192, 192)         # #C0C0C0
ACCENT = (0, 229, 160)             # #00E5A0

# Neural network visualizer
NODE_INPUT = (55, 138, 221)        # #378ADD
NODE_HIDDEN = (127, 119, 221)      # #7F77DD
NODE_OUTPUT = (239, 159, 39)       # #EF9F27
WEIGHT_POSITIVE = (0, 229, 160)    # #00E5A0
WEIGHT_NEGATIVE = (255, 71, 87)    # #FF4757
NODE_PULSE_WHITE = (255, 255, 255)

# Stats panel
GRID_LINE = (35, 35, 35)
GRAPH_LINE = (0, 229, 160)         # accent green
GRAPH_DOT_CURRENT = (239, 159, 39) # amber
BEST_EVER_LINE = (255, 71, 87)     # red dashed

# Species bird colors (cycle through)
SPECIES_COLORS = [
    (0, 229, 160),    # #00E5A0
    (123, 97, 255),   # #7B61FF
    (255, 107, 107),  # #FF6B6B
    (255, 217, 61),   # #FFD93D
    (78, 205, 196),   # #4ECDC4
    (255, 140, 200),  # #FF8CC8
    (168, 230, 207),  # #A8E6CF
    (255, 154, 60),   # #FF9A3C
]

# General
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (160, 160, 160)
