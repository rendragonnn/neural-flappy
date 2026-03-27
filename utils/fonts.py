"""
Font loader helper for Neural Flappy Bird.
Provides cached font loading with fallback to system monospace.
"""

import pygame

_font_cache: dict[tuple[str, int], pygame.font.Font] = {}


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Get a monospace font at the given size (cached)."""
    key = ("mono", size, bold)
    if key not in _font_cache:
        # Try common monospace fonts, fall back to pygame default
        mono_names = [
            "consolas", "couriernew", "courier", "lucidaconsole",
            "dejavusansmono", "liberationmono", "monospace",
        ]
        font = None
        for name in mono_names:
            try:
                font = pygame.font.SysFont(name, size, bold=bold)
                break
            except Exception:
                continue
        if font is None:
            font = pygame.font.Font(None, size)
            font.set_bold(bold)
        _font_cache[key] = font
    return _font_cache[key]


def get_title_font(size: int) -> pygame.font.Font:
    """Get a title/heading font (sans-serif)."""
    key = ("title", size)
    if key not in _font_cache:
        title_names = ["arial", "helvetica", "segoeui", "verdana"]
        font = None
        for name in title_names:
            try:
                font = pygame.font.SysFont(name, size, bold=True)
                break
            except Exception:
                continue
        if font is None:
            font = pygame.font.Font(None, size)
            font.set_bold(True)
        _font_cache[key] = font
    return _font_cache[key]
