import random
import time

from elements.Attributes import FontSettings
from elements.Elements import TextArea, TextDisplay
from elements.Types import SceneElement
from game import Challenge
from providers import ColorProvider, FileProvider
from scene import scene_manager
from utils import C


class TypingChallenge(Challenge):

	WORD_LENGTH = 5.5

	def __init__(self):
		super().__init__("Sweaty Keyboard", "Écris le texte affiché à l'écran le plus rapidement possible", "TypingLogo.png", True)
		self.start_time = None
		self.text_area = TextArea(FontSettings("resources/fonts/ArialMonoMTProRegular.TTF", 22, ColorProvider.get('fg')), pattern_color=ColorProvider.get('placeholder'))
		self.text_area.on("type", lambda: self.text_area.shake(6, 0.1, self.text_area.SHAKE_INSTANT))
		self.text_area.on("type", lambda: self.set_start_time() if len(self.text_area.get_content()) == 1 else None)
		self.text_area.on("text_complete", lambda: scene_manager.get_current_scene().end_challenge())

		self.wpm_display = TextDisplay(FontSettings("resources/fonts/Start.otf", 65, ColorProvider.get('fg')))
		self.wpm_display.on("tick", self.refresh_wpm)

	def set_start_time(self):
		self.start_time = time.time()

	def compute_wpm(self) -> float:
		delta = time.time() - self.start_time
		return 60 * (len(self.text_area.get_content()) / self.WORD_LENGTH) / delta

	def refresh_wpm(self):
		if self.start_time is None or time.time() - self.start_time == 0:
			wpm = 0
		else:
			wpm = self.compute_wpm()
		self.wpm_display.set_content(f"{wpm:.2f} WPM")

	def create_challenge_components(self) -> list[SceneElement]:
		return [
			self.text_area.set_max_width(int(0.8 * C.DISPLAY_SIZE[0])).set_anchor("midleft").set_relative_pos((0.1, 0.5)),
			self.wpm_display.set_anchor("center").set_relative_pos((0.5, 0.25))
		]

	def reset_challenge(self):
		super().reset_challenge()
		f = FileProvider.get('typing_statements.txt').splitlines()
		self.text_area.reset()
		self.text_area.set_pattern(f[random.randint(0, len(f) - 1)])
		self.start_time = None

	def format_result(self, result: float) -> str:
		return f"{result:.2f} WPM"

	def get_result_header(self) -> str:
		return "Typing Speed"

	def get_session_result(self) -> float:
		return self.compute_wpm()
