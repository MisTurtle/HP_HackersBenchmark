import time

from elements.Attributes import SpriteAnimation, FontSettings
from elements.Elements import Button, TextDisplay
from elements.Types import SceneElement
from game import Challenge
from providers import SpriteProvider, ColorProvider
from scene import scene_manager


class TimeMasterChallenge(Challenge):

	def __init__(self):
		super().__init__("Time Master", "Fait confiance à ton horloge interne et met ta maitrise du temps à l'épreuve", "TimeMasterLogo.png", True)
		self.clicked_times = []
		self.target_times = [1, 5, 10, 30]
		self.current_btn_id = 0

		font = FontSettings("resources/fonts/Start.otf", 50, ColorProvider.get('fg'))
		self.guideline_text = TextDisplay(font, content="Appuie une fois pour lancer un chronomètre et une deuxième fois après le temps indiqué sur le bouton. Plus tu es précis, plus tu gagnes de points !")
		self.guideline_text.set_relative_width(0.9).set_anchor("center").set_relative_pos((0.5, 0.2))

		self.button = Button(SpriteAnimation(SpriteProvider.get("Challenges/TimeMasterButtons.png"), [1, 1, 1, 1], [64, 64, 64, 64], None), on_click=self.handle_click)
		self.button.set_relative_width(0.25).set_anchor("center").set_relative_pos((0.5, 0.5))
		self.button.get_animation("click")._duration = 0.1

		self.feedback_text = TextDisplay(font.copy())

	def handle_click(self):
		if len(self.clicked_times) <= self.current_btn_id:
			# First click on this button
			self.clicked_times.append(time.time())
		else:
			# Compute delta
			delta = time.time() - self.clicked_times[self.current_btn_id]
			accuracy = max(0, 1 - abs(delta - self.target_times[self.current_btn_id]) / self.target_times[self.current_btn_id])
			# Compute accuracy
			self.clicked_times[int(self.current_btn_id)] = accuracy
			self.current_btn_id += 1
			if self.current_btn_id >= len(self.target_times):
				scene_manager.get_current_scene().end_challenge()
			else:
				self.button.get_spritesheet().set_animation_row(self.current_btn_id)

			# Update feedback
			self.feedback_text.set_content(f"Temps = {delta:.2f} sec. / Précision = {100*accuracy:.2f}%")
			self.feedback_text.get_display_settings().set_color(ColorProvider.get('error' if accuracy < 0.7 else 'success'))
			self.feedback_text.set_anchor("center").set_relative_pos((0.5, 0.8))

	def create_challenge_components(self) -> list[SceneElement]:
		return [self.guideline_text, self.button, self.feedback_text]

	def reset_challenge(self):
		self.clicked_times.clear()
		self.current_btn_id = 0
		self.button.get_spritesheet().set_animation_row(0)
		self.feedback_text.set_content("")

	def format_result(self, result: float) -> str:
		return f"{result*100:.2f}% accuracy"

	def get_result_header(self) -> str:
		return "Accuracy"

	def get_session_result(self) -> float:
		return sum(self.clicked_times) / len(self.target_times)
