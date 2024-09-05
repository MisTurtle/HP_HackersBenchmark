import random
import time

from elements.Attributes import SpriteAnimation, Animation, FontSettings
from elements.Elements import Button, TextDisplay
from elements.Types import SceneElement
from game import Challenge
from providers import SpriteProvider, ColorProvider
from scene import scene_manager
from utils import C


class ReactionTimeChallenge(Challenge):

	CLICK_FRAME_ID = 0

	CLICK_COUNT = 5  # clicks
	MIN_RED_TIME = 2.3  # s
	MAX_RED_TIME = 9.8  # s
	MAX_REACTION_TIME = 5  # s

	STATE_WAITING = 0
	STATE_RED = 1
	STATE_GREEN = 2

	def __init__(self):
		super().__init__("Quick as GPU", "Prouve que tes réflexes sont comparables à ceux d'une carte graphique", "ReactionTestLogo.png", False)
		self.deltas = []
		self.green_time = 0
		self.state = self.STATE_WAITING

		self.action_btn = Button(SpriteAnimation(SpriteProvider.get("Challenges/ReactionTestRectangle.png"), [1, 1, 1], [64, 64, 64], None), on_click=self.handle_click)
		self.action_btn.get_spritesheet().set_animation_row(2)
		self.action_btn.HOVER_AMPLIFY = 0
		self.action_btn.CLICK_DURATION = 0
		self.action_btn.get_animation("click")._duration = 0
		self.action_btn.add_animation("red_time", Animation(1).set_end_behavior(lambda anim: (self.set_green(), anim.reset())))
		self.action_btn.add_animation("timeout", Animation(self.MAX_REACTION_TIME).set_end_behavior(lambda anim: (self.timeout(), anim.reset())))

		font = FontSettings("resources/fonts/Start.otf", 50, ColorProvider.get('fg'))
		self.feedback_text = TextDisplay(font, content="")

	def refresh_action_sprite(self):
		sprite_id = {
			self.STATE_WAITING: 2,
			self.STATE_RED: 0,
			self.STATE_GREEN: 1
		}
		self.action_btn.get_spritesheet().set_animation_row(sprite_id[self.state])

	def set_feedback(self, status: str):
		self.feedback_text.set_content(status).set_relative_height(0.06).set_anchor("center").set_relative_pos((0.5, 0.2))
		if self.feedback_text.width >= 0.8 * C.DISPLAY_SIZE[0]:
			self.feedback_text.set_relative_width(0.8)

	def handle_click(self):
		if self.CLICK_FRAME_ID == C.FRAME_ID:
			return
		self.CLICK_FRAME_ID = C.FRAME_ID

		anim = self.action_btn.get_animation("red_time")
		tout_anim = self.action_btn.get_animation("timeout")
		if self.state == self.STATE_WAITING:
			self.state = self.STATE_RED
			anim._duration = self.MIN_RED_TIME + random.random() * (self.MAX_RED_TIME - self.MIN_RED_TIME)
			anim.reset().start()
		elif self.state == self.STATE_RED:
			self.state = self.STATE_WAITING
			self.register_delta(-1)
			anim.reset()
			tout_anim.reset()
			self.set_feedback(f"[{len(self.deltas)}/{self.CLICK_COUNT}] Trop tôt = {self.MAX_REACTION_TIME * 1000}ms")
		elif self.state == self.STATE_GREEN:
			self.state = self.STATE_WAITING
			d = time.time() - self.green_time
			self.register_delta(d)
			tout_anim.reset()
			self.set_feedback(f"[{len(self.deltas)}/{self.CLICK_COUNT}] Temps de réaction: {self.format_result(d)}")

		self.refresh_action_sprite()

	def register_delta(self, delta: float):
		self.deltas.append(delta)
		if len(self.deltas) >= self.CLICK_COUNT:
			scene_manager.get_current_scene().end_challenge()

	def timeout(self):
		self.register_delta(-1)
		self.set_feedback(f"[{len(self.deltas)}/{self.CLICK_COUNT}] Trop long = {self.MAX_REACTION_TIME * 1000}ms")
		self.state = self.STATE_WAITING
		self.refresh_action_sprite()

	def set_green(self):
		self.state = self.STATE_GREEN
		self.refresh_action_sprite()
		self.green_time = time.time()
		self.action_btn.get_animation("timeout").reset().start()

	def format_result(self, result: float) -> str:
		return f"{1000*result:.0f} ms"

	def create_challenge_components(self) -> list[SceneElement]:
		return [self.feedback_text, self.action_btn.set_relative_width(0.7).set_anchor("center").set_relative_pos((0.5, 0.55))]

	def get_result_header(self) -> str:
		return "Reaction Time"

	def get_session_result(self) -> float:
		return sum(map(lambda x: x if x > 0 else self.MAX_REACTION_TIME, self.deltas)) / len(self.deltas)

	def reset_challenge(self):
		self.deltas = []
		self.green_time = 0
		self.state = self.STATE_WAITING
		self.refresh_action_sprite()
		self.feedback_text.set_content("")
		self.action_btn.get_animation("red_time").reset()
		self.action_btn.get_animation("timeout").reset()
