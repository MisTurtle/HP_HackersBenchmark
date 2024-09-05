import random

import pygame

from elements.Attributes import Animation, FontSettings
from elements.Elements import DrawingGrid, TextDisplay, DrawingCell
from elements.Types import SceneElement, Hoverable
from game import Challenge
from providers import ColorProvider
from scene import scene_manager
from utils import C


class SequenceMemoryChallenge(Challenge):

	GRID_SIZE = 4
	PLAY_STEP_DURATION = 0.5
	SHOW_PLAY_DURATION = 0.2

	def __init__(self):
		super().__init__("Sequence Mastermind", "Souviens-toi des séquences passant à l'écran", "SequenceLogo.png", True)
		self.LAST_FRAME_CLICK = 0
		self.sequence: list[tuple[int, int]] = []
		self.played = 0
		self.replayed_steps = 0

		self.grid = DrawingGrid(
			(self.GRID_SIZE, self.GRID_SIZE),
			hover_color=ColorProvider.get('bg'),
			filled_color=pygame.Color(255, 255, 255)
		)
		self.grid.set_anchor("center").set_relative_pos((0.5, 0.5)).set_relative_height(0.5)
		self.grid.add_animation("play_sequence", Animation(self.PLAY_STEP_DURATION).set_end_behavior(lambda anim: (anim.reverse(), self.play_next_step())))
		self.grid.add_animation("show_play", Animation(self.SHOW_PLAY_DURATION).set_end_behavior(lambda anim: (self.set_grid_enabled(True), self.grid.clear_grid(), anim.reset())))
		for el in self.grid.get_elements():
			if isinstance(el, DrawingCell):
				el.on("click", lambda: (self.grid.clear_grid(), self.append_step()) if len(self.sequence) == 0 else self.check_move())

		font = FontSettings("resources/fonts/Start.otf", 50, ColorProvider.get('fg'))
		self.feedback_text = TextDisplay(font, content="")

	def set_feedback(self, status: str):
		self.feedback_text.set_content(status).set_relative_height(0.06).set_anchor("center").set_relative_pos((0.5, 0.2))
		if self.feedback_text.width >= 0.8 * C.DISPLAY_SIZE[0]:
			self.feedback_text.set_relative_width(0.8)

	def set_grid_enabled(self, val: bool):
		self.grid.set_enabled(val)
		for el in self.grid.get_elements():
			if isinstance(el, Hoverable):
				el.set_enabled(val)

	def append_step(self):
		if len(self.sequence) == 0:
			self.sequence.append((random.randint(0, self.GRID_SIZE - 1), random.randint(0, self.GRID_SIZE - 1)))
		else:
			seq = self.sequence[-1]
			while seq == self.sequence[-1]:
				seq = random.randint(0, self.GRID_SIZE - 1), random.randint(0, self.GRID_SIZE - 1)
			self.sequence.append(seq)
		self.play_sequence()
		self.played = 0
		# print("New step : ", self.sequence[-1])

	def play_sequence(self):
		self.set_grid_enabled(False)
		self.replayed_steps = 0
		self.grid.get_animation("play_sequence").reset().start()
		self.set_feedback("Souviens-toi de la séquence qui s'affiche à l'écran")

	def play_next_step(self):
		self.grid.clear_grid()
		if self.replayed_steps >= len(self.sequence):
			self.stop_replay()
			self.set_grid_enabled(True)
			self.set_feedback(f"A toi de jouer! Séquence de taille {len(self.sequence)}")
		else:
			step_pos = self.sequence[self.replayed_steps]
			self.grid.get_elements()[step_pos[1] * self.GRID_SIZE + step_pos[0]].set_filled(True)
			self.replayed_steps += 1

	def stop_replay(self):
		self.grid.clear_grid()
		self.replayed_steps = 0
		self.grid.get_animation("play_sequence").reset()
		self.grid.get_animation("show_play").reset()
		self.set_grid_enabled(True)

	def format_result(self, result: float) -> str:
		return f"{result:.0f}"

	def create_challenge_components(self) -> list[SceneElement]:
		return [self.grid, self.feedback_text]

	def get_result_header(self) -> str:
		return "Sequence Length"

	def get_session_result(self) -> float:
		return len(self.sequence) - 1

	def reset_challenge(self):
		self.sequence.clear()
		self.stop_replay()
		self.set_grid_enabled(True)
		self.set_feedback("Appuie sur la grille pour commencer !")

	def check_move(self):
		if C.FRAME_ID == self.LAST_FRAME_CLICK:
			return
		self.LAST_FRAME_CLICK = C.FRAME_ID
		cell_id = 0
		for el in self.grid.get_elements():
			if isinstance(el, DrawingCell):
				if el.is_filled():
					break
				else:
					cell_id += 1
		x, y = cell_id % self.GRID_SIZE, cell_id // self.GRID_SIZE
		if (x, y) != self.sequence[self.played]:
			self.on_fail()
		else:
			self.on_step()

	def on_fail(self):
		self.set_grid_enabled(False)
		self.grid.blink(ColorProvider.get("error"), lambda: scene_manager.get_current_scene().end_challenge())

	def on_step(self):
		self.played += 1
		if self.played == len(self.sequence):
			self.set_grid_enabled(False)
			self.grid.blink(ColorProvider.get("success"), self.append_step)
		else:
			self.set_grid_enabled(False)
			self.grid.get_animation("show_play").start()
