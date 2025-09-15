
import os
import sys
import time

if getattr(sys, 'frozen', False):
	os.chdir(sys._MEIPASS)
	import pyi_splash
	pyi_splash.close()

import random
import time
import pygame
from hb_screens.challenges.ConflictsSolverChallenge import ConflictsSolverChallenge
from hb_screens.challenges.TimeMasterChallenge import TimeMasterChallenge
from hb_screens.challenges.BugHunterChallenge import BugHunterChallenge
from hb_screens.challenges.TypingFrenzyChallenge import TypingFrenzyChallenge
from hb_screens.challenges.MindTripTimeChallenge import MindTripTimeChallenge
from hb_screens.screen_result import ScreenAction
from hb_screens.synopsis_screen import SynopsisScreen
from hb_screens.welcome_screen import WelcomeScreen
from hb_types.observers import Observer
from hb_types.scenes import Scene
import hb_utils.factories
from hb_utils.info import PlayerInfo
from hb_utils.maths import ease_in_out


pygame.init()
surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Honeypot Hacker's Benchmark - September 2025")
screen_rect = surface.get_rect()

hb_utils.factories.init()

clock = pygame.time.Clock()
fps, dt = 60, 0


class GameTimeline(Observer):

    SEQUENCE_ORDER = [
        WelcomeScreen, 
        SynopsisScreen, 
        MindTripTimeChallenge,
        BugHunterChallenge,
        TypingFrenzyChallenge,
        TimeMasterChallenge,
        ConflictsSolverChallenge
    ]

    def __init__(self, original_scene: Scene):
        super().__init__()
        self.current_scene = original_scene
        self.current_scene.attach(self)
        self.next_scene = None
    
    def update(self, subject: Scene):
        """
        For now, an update means the subject scene has closed and the following scene should be open. Replays might need this to be tweaked
        """
        if subject.action == ScreenAction.QUIT_PROGRAM:
            global running
            running = False
            return
        
        if subject.action == ScreenAction.LOAD_NEXT:
            next_screen = GameTimeline.SEQUENCE_ORDER[(GameTimeline.SEQUENCE_ORDER.index(subject.__class__) + 1) % len(GameTimeline.SEQUENCE_ORDER)]
        elif subject.action == ScreenAction.LOAD_PREVIOUS:
            next_screen = GameTimeline.SEQUENCE_ORDER[(GameTimeline.SEQUENCE_ORDER.index(subject.__class__) - 1) % len(GameTimeline.SEQUENCE_ORDER)]
        
        self.current_scene.detach(self)
        self.next_scene = next_screen(self.current_scene.player_info)
        
        self.current_scene.bg_color.animate(
            self.current_scene.bg_color.value,
            self.next_scene.bg_color.value,
            self.current_scene.MAX_SCENE_TRANSITION_DURATION,
            False,
            after=self.perform_scene_switch,
            easing=ease_in_out
        )
    
    def perform_scene_switch(self):
        game_timeline.current_scene, game_timeline.next_scene = game_timeline.next_scene, None
        self.current_scene.attach(self)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


def glitch_shader(screen: pygame.Surface, t: float):
	delay = 15
	duration = 0.5
	disparity = 15, 25
	block_unit_size = 10, 10
	if round((t + random.randint(disparity[0], disparity[1]) / 10) / duration) % delay != 0:
		return

	def extract_sub_surfaces(_block_size: tuple[int, int]):
		_pos_a = random.randint(_block_size[0] * 2, screen.get_width() - _block_size[0] * 2), random.randint(_block_size[1] * 2, screen.get_height() - _block_size[1] * 2)
		_pos_b = _pos_a[0] + 0.5 * block_size[0] * (-1 if random.random() < 0.5 else 1), _pos_a[1] + block_size[1] * random.randint(-1, 1)
		_frame_a, _frame_b = screen.subsurface(_pos_a, _block_size).copy(), screen.subsurface(_pos_b, _block_size).copy()
		return _frame_a, _frame_b, _pos_a, _pos_b

	for _ in range(random.randint(20, 35)):
		block_size = random.randint(2, 8) * block_unit_size[0], block_unit_size[1]
		frame_a, frame_b, pos_a, pos_b = extract_sub_surfaces(block_size)
		screen.blit(frame_a, pos_b)
		screen.blit(frame_b, pos_a)


game_timeline = GameTimeline(WelcomeScreen(player_info=PlayerInfo(username="Karma")))
running = True
while running:
    frame_start = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            game_timeline.current_scene.handle_event(event)
    
    surface.fill(game_timeline.current_scene.bg_color.value)
    game_timeline.current_scene.update(dt / 1000)
    game_timeline.current_scene.draw(surface)
    glitch_shader(surface, frame_start)
    pygame.display.flip()
    dt = clock.tick(fps)

