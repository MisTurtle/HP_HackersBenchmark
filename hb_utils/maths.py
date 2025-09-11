from typing import Tuple, Union

import pygame


Numeric = Union[float, int]
Color = Tuple[int, int, int]
Animatable = Union[Numeric, Color]

def lerp(start: Animatable, end: Animatable, t: float) -> Animatable:
    """Linear interpolation supporting numbers and colors."""
    if isinstance(start, tuple):
        start = pygame.color.Color(*start)
    if isinstance(end, tuple):
        end = pygame.color.Color(*end)
    if isinstance(start, pygame.color.Color) and isinstance(end, pygame.color.Color):
        _ = lambda s, e: min(255, max(0, int(s + (e - s) * t)))
        return pygame.color.Color(_(start.r, end.r), _(start.g, end.g), _(start.b, end.b))
    else:
        return start + (end - start) * t

def ease_in_out(t: float) -> float:
    """Ease in-out interpolation (smooth start and end)."""
    return t * t * (3 - 2 * t)

def auto_width(rel_height: float, original_size: tuple[int, int], container_size: tuple[int, int]):
    if original_size[1] == 0:
        return 0
    final_height = rel_height * container_size[1]
    original_ratio = original_size[0] / original_size[1]
    target_width = original_ratio * final_height
    return target_width / container_size[0]

def auto_height(rel_width: float, original_size: tuple[int, int], container_size: tuple[int, int]):
    if original_size[0] == 0:
        return 0
    final_width = rel_width * container_size[0]
    original_ratio = original_size[1] / original_size[0]
    target_height = original_ratio * final_width
    return target_height / container_size[1]
