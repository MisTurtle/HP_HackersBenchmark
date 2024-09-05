import os
import random
import sys
import time

if getattr(sys, 'frozen', False):
	os.chdir(sys._MEIPASS)
	import pyi_splash
	pyi_splash.close()

import contextlib
with contextlib.redirect_stdout(None):
	import pygame

import providers
from typing import Callable, Any

from game import challenge_manager
from scene import scene_manager
from scene.all.EndScene import EndScene
from scene.all.GameScene import GameScene
from scene.all.MenuScene import MenuScene
from utils import AppState, C, Provider

# Initialize pygame and compute screen size
pygame.init()
info = pygame.display.Info()
C.DISPLAY_SIZE = info.current_w, info.current_h
C.DISPLAY_RECT = pygame.Rect((0, 0), C.DISPLAY_SIZE)
screen = pygame.display.set_mode(C.DISPLAY_SIZE, pygame.FULLSCREEN)

# Initialize base providers (font, sprite, ...)
providers.init()

# Initialize window icon and title
pygame.display.set_caption("FuriousHacker by Honeypot")
pygame.display.set_icon(providers.SpriteProvider.get('HoneyPot_Logo_NOBG_Centered.png'))

# Register scenes
scene_manager.set(scene_manager.MENU_SCENE, MenuScene())
game_scene = GameScene()
scene_manager.set(scene_manager.GAME_SCENE, game_scene)
scene_manager.set(scene_manager.END_SCENE, EndScene())

challenge_manager.init_challenges()

# Create Scene Manager
scene_manager.set_active_scene(scene_manager.MENU_SCENE)

# Register event handlers
EventHandlers: Provider[int, Callable[[pygame.event.Event], Any]] = Provider[
	int, Callable[[pygame.event.Event], None]]()
EventHandlers.set(pygame.QUIT, lambda _: AppState.stop())
EventHandlers.set(pygame.MOUSEMOTION, lambda ev: scene_manager.set_cursor(ev.pos))
EventHandlers.set(pygame.MOUSEBUTTONDOWN, lambda ev: scene_manager.handle_click(ev.pos, ev.button))
EventHandlers.set(pygame.MOUSEBUTTONUP, lambda ev: scene_manager.handle_release(ev.button))
EventHandlers.set(pygame.KEYDOWN, lambda ev: scene_manager.type(ev.unicode))


# Register main screen shader
def glitch_shader(screen: pygame.Surface, t: float):
	delay = 15
	duration = 0.5
	disparity = 10, 25
	block_unit_size = 10, 10
	if not C.FORCE_GLITCH_SHADER and round((t + random.randint(disparity[0], disparity[1]) / 10) / duration) % delay != 0:
		return

	def extract_sub_surfaces(_block_size: tuple[int, int]):
		_pos_a = random.randint(_block_size[0] * 2, screen.get_width() - _block_size[0] * 2), random.randint(_block_size[1] * 2, screen.get_height() - _block_size[1] * 2)
		_pos_b = _pos_a[0] + 0.5 * block_size[0] * (-1 if random.random() < 0.5 else 1), _pos_a[1] + block_size[1] * random.randint(-1, 1)
		_frame_a, _frame_b = screen.subsurface(_pos_a, _block_size).copy(), screen.subsurface(_pos_b, _block_size).copy()
		# dark = pygame.Surface(_frame_b.get_size())
		# dark.set_alpha(random.randint(30, 60))
		# dark.fill((0, 0, 0))
		# _frame_b.blit(dark, (0, 0))
		return _frame_a, _frame_b, _pos_a, _pos_b

	for _ in range(random.randint(20, 35)):
		block_size = random.randint(2, 8) * block_unit_size[0], block_unit_size[1]
		frame_a, frame_b, pos_a, pos_b = extract_sub_surfaces(block_size)
		screen.blit(frame_a, pos_b)
		screen.blit(frame_b, pos_a)


providers.ShaderProvider.set("glitch", glitch_shader)

# Begin main loop
clock = pygame.time.Clock()
elapsed = .0
while AppState.is_running() and scene_manager.get_current_scene() is not None:
	frame_start = time.time()
	for event in pygame.event.get():
		EventHandlers.get(event.type, lambda _: None)(event)
	scene_manager.get_current_scene().update(elapsed / 1000)
	scene_manager.get_current_scene().draw(screen)
	for shader in providers.ShaderProvider.get_all().values():
		shader(screen, frame_start)
	pygame.display.update()
	C.FRAME_ID += 1
	elapsed = clock.tick(AppState.get_target_frame_rate())
	AppState.register_frame_time(1000 / elapsed)
