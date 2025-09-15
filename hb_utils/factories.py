import os
from typing import Callable, Any

import pygame
from hb_types.factory import Provider, LoadOnGetProvider


def __load_colors():
	ColorProvider.set("bg", pygame.Color(0xDE, 0xDE, 0xDE))
	ColorProvider.set("bg_dark", pygame.Color(0x10, 0x10, 0x10))
	ColorProvider.set("bg_dark_lighter", pygame.Color(0x30, 0x30, 0x30))
	ColorProvider.set("fg", pygame.Color(0xAD, 0x21, 0x8D))
	ColorProvider.set("fg2", pygame.Color(0xED, 0x91, 0xD8))
	ColorProvider.set("placeholder", pygame.Color(0xbE, 0xbe, 0xbe))
	ColorProvider.set("success", pygame.Color(0xA8, 0xFF, 0x99))
	ColorProvider.set("success2", pygame.Color(0x69, 0xFF, 0x5C))
	ColorProvider.set("error", pygame.Color(0xFF, 0x99, 0x99))
	ColorProvider.set("error2", pygame.Color(0xFF, 0x5C, 0x5C))


def init():
	pygame.font.init()
	__load_colors()


FontProvider: Provider[str, pygame.font.Font] = LoadOnGetProvider[(str, int), pygame.font.Font](lambda name_and_size: pygame.font.Font("resources/fonts/" + name_and_size[0], int(name_and_size[1] * pygame.display.get_surface().get_width() / 1920)))
SpriteProvider: Provider[str, pygame.Surface] = LoadOnGetProvider[str, pygame.Surface](lambda x: pygame.image.load("resources/sprites/" + x))
ColorProvider: Provider[str, pygame.color.Color] = Provider[str, pygame.color.Color]()
ShaderProvider: Provider[str, Callable[[pygame.Surface, float], Any]] = Provider[str, Callable[[pygame.Surface, float], Any]]()


def read_file(path: str) -> str:
	with open(path, 'r', encoding='utf-8') as f:
		return f.read()


FileProvider: Provider[str, str] = LoadOnGetProvider[str, str](lambda x: read_file("resources/files/" + x))

init()