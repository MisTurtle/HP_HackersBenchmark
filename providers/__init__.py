import os
from typing import Callable, Any

import pygame
from utils import Provider, LoadOnGetProvider


def __init_fonts():
	for file_name in os.listdir("resources/fonts"):
		FontProvider.set(file_name, pygame.font.Font("resources/fonts/" + file_name, 32))


def __load_colors():
	# ColorProvider.set("bg", pygame.Color(0x19, 0x16, 0x2b))
	# ColorProvider.set("fg", pygame.Color(0x67, 0x8c, 0xd6))
	# # ColorProvider.set("fg", pygame.Color(0xa2, 0xba, 0xeb))
	# ColorProvider.set("placeholder", pygame.Color(0x2e, 0x42, 0x61))
	# ColorProvider.set("fg2", pygame.Color(0x25, 0x32, 0x4d))
	# ColorProvider.set("category", pygame.Color(0x88, 0xf7, 0x5c))
	# ColorProvider.set("error", pygame.Color(0xf2, 0x74, 0x55))
	# ColorProvider.set("star_level_0", pygame.Color(0xff, 0xff, 0xff))
	# ColorProvider.set("star_level_1", pygame.Color(0x91, 0xed, 0x64))
	# ColorProvider.set("star_level_2", pygame.Color(0xbb, 0xed, 0x64))
	# ColorProvider.set("star_level_3", pygame.Color(0xed, 0xe6, 0x64))
	# ColorProvider.set("star_level_4", pygame.Color(0xed, 0xa4, 0x64))
	# ColorProvider.set("star_level_5", pygame.Color(0xed, 0x64, 0x64))
	# ColorProvider.set("success", pygame.Color(0x88, 0xf7, 0x5c))
	# ColorProvider.set("failure", pygame.Color(0xf7, 0x78, 0x5c))
	ColorProvider.set("bg", pygame.Color(0x00, 0x00, 0x00))
	ColorProvider.set("fg", pygame.Color(0xFF, 0xFF, 0xFF))
	# ColorProvider.set("fg", pygame.Color(0xa2, 0xba, 0xeb))
	ColorProvider.set("placeholder", pygame.Color(0xAA, 0xAA, 0xAA))
	ColorProvider.set("fg2", pygame.Color(0xEE, 0xEE, 0xEE))
	ColorProvider.set("category", pygame.Color(0x88, 0xf7, 0x5c))
	ColorProvider.set("error", pygame.Color(0xf2, 0x74, 0x55))
	ColorProvider.set("star_level_0", pygame.Color(0xff, 0xff, 0xff))
	ColorProvider.set("star_level_1", pygame.Color(0x91, 0xed, 0x64))
	ColorProvider.set("star_level_2", pygame.Color(0xbb, 0xed, 0x64))
	ColorProvider.set("star_level_3", pygame.Color(0xed, 0xe6, 0x64))
	ColorProvider.set("star_level_4", pygame.Color(0xed, 0xa4, 0x64))
	ColorProvider.set("star_level_5", pygame.Color(0xed, 0x64, 0x64))
	ColorProvider.set("success", pygame.Color(0x88, 0xf7, 0x5c))
	ColorProvider.set("failure", pygame.Color(0xf7, 0x78, 0x5c))


def init():
	pygame.font.init()
	__init_fonts()
	__load_colors()


FontProvider: Provider[str, pygame.font.Font] = Provider[str, pygame.font.Font]()
SpriteProvider: Provider[str, pygame.Surface] = LoadOnGetProvider[str, pygame.Surface](
	lambda x: pygame.image.load("resources/sprites/" + x)
)
ColorProvider: Provider[str, pygame.color.Color] = Provider[str, pygame.color.Color]()
ShaderProvider: Provider[str, Callable[[pygame.Surface, float], Any]] = Provider[str, Callable[[pygame.Surface, float], Any]]()


def read_file(path: str) -> str:
	with open(path, 'r', encoding='utf-8') as f:
		return f.read()


FileProvider: Provider[str, str] = LoadOnGetProvider[str, str](lambda x: read_file("resources/files/" + x))
