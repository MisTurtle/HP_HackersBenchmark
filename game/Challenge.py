from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from scene.all.GameScene import GameScene

from abc import ABC, abstractmethod

from elements.Attributes import FontSettings, SpriteAnimation, PulseSettings
from elements.Elements import TextDisplay, Button, Sprite, PulsingText
from elements.Types import SceneElement
from providers import ColorProvider, SpriteProvider
from scene import scene_manager
from utils import C
from utils.leaderboard import Leaderboard, LeaderboardEntry


class Challenge(ABC):

	def __init__(self, name: str, description: str, logo_file_name: str, descending_lb: bool):
		self._name = name
		self._description = description
		self._logo_sprite = Sprite(SpriteAnimation(SpriteProvider.get("Challenges/" + logo_file_name), [20], [0.04], None).set_mode(SpriteAnimation.MODE_CIRCULAR))
		self._logo_sprite.set_relative_height(0.22).set_anchor("center").set_relative_pos((0.5, 0.3))
		self.title_display, self.description_display, self.leaderboard_display = None, None, None
		self.leaderboard = Leaderboard(name.lower().replace(" ", "_"), descending_lb)

	def get_name(self) -> str:
		return self._name

	def get_description(self) -> str:
		return self._description

	@abstractmethod
	def format_result(self, result: float) -> str:
		pass

	def create_title(self) -> list[SceneElement]:
		if self.title_display is None:
			self.title_display = TextDisplay(FontSettings("resources/fonts/Code.ttf", 75, ColorProvider.get("fg")), content=">/" + self.get_name())
			self.title_display.set_anchor("midtop").set_relative_pos((0.5, 0.01))
		return [self.title_display]

	def create_description(self) -> list[SceneElement]:
		if self.description_display is None:
			self.description_display = TextDisplay(FontSettings("resources/fonts/Start.otf", 50, ColorProvider.get("fg")), content=self.get_description())
			self.description_display.set_anchor("midtop").set_relative_pos((0.5, 0.01)).move((0, self.title_display.height))
		return [self.description_display]

	def create_leaderboard(self) -> list[SceneElement]:
		if self.leaderboard_display is None:
			font_settings = FontSettings("resources/fonts/Code.ttf", 50, ColorProvider.get("fg"))
			self.leaderboard_display = TextDisplay(font_settings)
		top = self.leaderboard.get_top(10)

		lines = []
		for rank, entry in enumerate(top):
			prefix = f"#{rank + 1} - {entry.get_name()}"
			lines.append(prefix + (" " * max(1, (21 - len(prefix)))) + "-->" + (" " * 4) + self.format_result(entry.get_score()))

		if len(lines) == 0:
			return [self.leaderboard_display]

		self.leaderboard_display.set_content("\n".join(lines))

		# Position leaderboards on screen
		max_unit_width = 0.7
		self.leaderboard_display.set_relative_height(0.30)
		if self.leaderboard_display.width > max_unit_width * C.DISPLAY_SIZE[0]:
			self.leaderboard_display.set_relative_width(max_unit_width)

		self.leaderboard_display.set_anchor("midtop").set_relative_pos((0.5, 0.43))

		return [self.leaderboard_display]

	@abstractmethod
	def create_challenge_components(self) -> list[SceneElement]:
		pass

	def create_reset_button(self) -> list[SceneElement]:
		return [Challenge.restart_btn.set_click_callback(lambda: scene_manager.get_current_scene().start_challenge()).set_anchor("center").set_relative_pos((0.25, 0.95)).set_relative_width(0.25)]

	def create_close_button(self) -> list[SceneElement]:
		def close_handler():
			self.reset_challenge()
			scene_manager.get_current_scene().on_set_active()

		return [Challenge.close_btn.set_anchor("center").set_relative_pos((0.75, 0.95)).set_click_callback(close_handler).set_relative_width(0.25)]

	def create_control_buttons(self) -> list[SceneElement]:
		return self.create_reset_button() + self.create_close_button()

	def create_chall_display_elements(self) -> list[SceneElement]:
		return self.create_title() + self.create_description() + [self._logo_sprite]

	def create_chall_display_elements_and_lb(self) -> list[SceneElement]:
		return self.create_title() + self.create_description() + [self._logo_sprite] + self.create_leaderboard()

	def create_chall_session_elements(self) -> list[SceneElement]:
		return self.create_title() + self.create_description() + self.create_challenge_components() + self.create_control_buttons()

	def create_result_display_elements(self, result: float, improved: bool, best: float, rank: int) -> list[SceneElement]:
		font_settings = FontSettings("fonts/Code.ttf", 75, ColorProvider.get('fg'))
		keys_text = TextDisplay(font_settings, content=f"{self.get_result_header()}\n\nBest {self.get_result_header()}\n\nRank")
		values_text = TextDisplay(font_settings, content=f":  {self.format_result(result)}\n\n:  {self.format_result(best)}\n\n:  #{rank}")
		if keys_text.width > 0.2 * C.DISPLAY_SIZE[0]:
			keys_text.set_relative_width(0.2)
		if values_text.width > 0.2 * C.DISPLAY_SIZE[0]:
			values_text.set_relative_width(0.2)
		keys_text.set_anchor("midleft").set_relative_pos((0.15, 0.5))
		values_text.set_anchor("midright").set_relative_pos((0.85, 0.5))

		improved_text = PulsingText(font_settings.copy())
		if improved:
			text = ["High Score !", "Masterclass !", "Awesome !", "Amazing !", "Good Job !", "Nicely Done !", "Oh Dear !"]
			improved_text.set_content(text[random.randint(0, len(text) - 1)]).get_display_settings().set_color(ColorProvider.get('success'))
			improved_text.set_pulse_settings(PulseSettings(0.5, 0.2, (0.9, 0.9)))
		else:
			text = ["Too Bad !", "So Close !", "Close Call !", "Better luck next time !", "You can do better !", "No way..."]
			improved_text.set_content(text[random.randint(0, len(text) - 1)]).get_display_settings().set_color(ColorProvider.get('error'))
			improved_text.set_pulse_settings(PulseSettings(1.5, 0.2, (0.9, 0.9)))

		if improved_text.width >= 0.5 * C.DISPLAY_SIZE[0]:
			improved_text.set_relative_width(0.5)
		improved_text.set_anchor("center").set_relative_pos((0.5, 0.75))

		return self.create_title() + self.create_description() + [self._logo_sprite] + [keys_text, values_text, improved_text] + self.create_control_buttons()

	def submit_score(self, score: float) -> tuple[bool, int]:
		"""
		:param score: Player score
		:return: (improved, rank)
		"""
		scene: GameScene = scene_manager.get_current_scene()
		entry = LeaderboardEntry(scene.current_player, score)
		improved = self.leaderboard.improves(entry)
		if improved:
			self.leaderboard.add_score(entry)
		return improved, self.leaderboard.get_rank(scene.current_player)

	@abstractmethod
	def get_result_header(self) -> str:
		"""
		:return: a field header introducing the player's score (e.i. Typing speed for a typing test, Reaction time for a reaction time, ...)
		"""
		pass

	@abstractmethod
	def get_session_result(self) -> float:
		pass

	@abstractmethod
	def reset_challenge(self):
		pass


Challenge.close_btn = Button(SpriteAnimation(SpriteProvider.get("Btn_Fermer.png"), [1], [64], (570, 60)), on_click=lambda: None)
Challenge.restart_btn = Button(SpriteAnimation(SpriteProvider.get("Btn_Restart.png"), [1], [64], (570, 60)), on_click=lambda: None)
