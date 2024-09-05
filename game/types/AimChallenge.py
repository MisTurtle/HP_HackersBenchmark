import random
import time

from elements.Attributes import FontSettings, SpriteAnimation
from elements.Elements import Timer, TextDisplay, Button
from elements.Types import SceneElement
from game import Challenge
from providers import ColorProvider, SpriteProvider
from scene import scene_manager
from utils import C


class AimChallenge(Challenge):

	TARGET_COUNT = 20

	def __init__(self):
		super().__init__("Sharp Aim", "Clique les bugs le plus rapidement possible", "AimChallengeLogo.png", False)
		self.target_hit = 0
		self.last_clicked_frame = 0  # Prevent multiple clicks in a single frame

		self.timer = Timer(FontSettings("resources/fonts/Code.ttf", 65, ColorProvider.get('fg')), clock=0, limit=[0, 5 * 60])
		self.timer.set_relative_width(0.33).set_anchor("center").set_relative_pos((0.5, 0.8))

		self.target_count_display = TextDisplay(FontSettings("resources/fonts/Start.otf", 65, ColorProvider.get('fg')))
		self.refresh_target_count_display()

		self.bug = Button(SpriteAnimation(SpriteProvider.get("Challenges/AimBug.png"), [1], [64], None), on_click=self.on_bug_click)
		self.bug.on("move", lambda: self.bug.set_hovered(False))
		self.bug.set_one_click_per_frame(True)
		self.bug.set_zoom((0.08, 0.08)).set_anchor("center").set_relative_pos((0.5, 0.5))
		self.bug.HOVER_AMPLIFY = 0
		self.bug.CLICK_DURATION = 0
		self.bug.get_animation("click")._duration = 0

	def on_bug_click(self):
		if self.last_clicked_frame == C.FRAME_ID:
			return
		self.last_clicked_frame = C.FRAME_ID
		if not self.timer.running:
			self.timer.start()
		else:
			self.target_hit += 1
			if self.target_hit >= self.TARGET_COUNT:
				scene_manager.get_current_scene().end_challenge()
			else:
				self.refresh_target_count_display()
		self.bug.set_relative_pos((random.randint(30, 970) / 1000, random.randint(30, 850) / 1000))

	def refresh_target_count_display(self):
		self.target_count_display.set_content(f"Bugs éliminés : {self.target_hit}/{self.TARGET_COUNT}")
		if self.target_count_display.width > 0.5 * C.DISPLAY_SIZE[0]:
			self.target_count_display.set_relative_width(0.5)
		self.target_count_display.set_anchor("center").set_relative_pos((0.5, 0.2))

	def create_challenge_components(self) -> list[SceneElement]:
		return [self.timer, self.target_count_display, self.bug]

	def reset_challenge(self):
		self.target_hit = 0
		self.timer.reset().pause()
		self.bug.set_relative_pos((0.5, 0.5))
		self.refresh_target_count_display()

	def format_result(self, result: float) -> str:
		return f"{1000 * result:.0f} ms/bug"

	def get_result_header(self) -> str:
		return "Bug Lifetime"

	def get_session_result(self) -> float:
		return self.timer.get_passed_time() / self.TARGET_COUNT
