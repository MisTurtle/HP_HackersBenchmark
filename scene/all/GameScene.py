from elements.Attributes import SpriteAnimation, FontSettings, PulseSettings
from elements.Elements import Button, TextArea, TextDisplay, PulsingImage, Sprite
from game import challenge_manager
from providers import ColorProvider, SpriteProvider
from scene import Scene
from utils import C


class GameScene(Scene):

	CONTROL_MARGIN = 30  # px

	def __init__(self):
		super().__init__()
		self.current_challenge = 0
		self.current_player = ""

		# Create comm elements
		self.honeypot_logo = PulsingImage(
			SpriteAnimation(SpriteProvider.get("HoneyPot_Logo_NOBG_Centered.png"), [1], [60], (1051, 1138))
		).set_pulse_settings(PulseSettings(period=0.83, amplitude=0.05, base=(1, 1))).set_relative_height(0.33).set_anchor("center").set_relative_pos((0.5, 0.25))
		self.discord_qr_code = Sprite(
			SpriteAnimation(SpriteProvider.get("HoneyPot_QR_Discord.png"), [1], [60], None)
		).set_relative_height(0.33).set_anchor("center").set_relative_pos((0.35, 0.7))
		self.insta_qr_code = Sprite(
			SpriteAnimation(SpriteProvider.get("HoneyPot_QR_Insta.png"), [1], [60], None)
		).set_relative_height(0.33).set_anchor("center").set_relative_pos((0.65, 0.7))

		# Create Challenge Controls
		self.start_chall_btn = Button(SpriteAnimation(SpriteProvider.get("Challenges/Btn_StartChallenge.png"), [20], [0.05], None).set_mode(SpriteAnimation.MODE_CIRCULAR), on_click=self.display_nickname_input_screen)
		self.start_chall_btn.set_relative_width(0.20).set_anchor("center").set_relative_pos((0.5, 0.95)).move((0, -self.start_chall_btn.height / 2))

		self.prev_chall_btn = Button(SpriteAnimation(SpriteProvider.get("Arrows.png"), [1, 1], [64, 64], (228, int(599/2) + 1)), on_click=lambda: self.display_prev_challenge())
		self.next_chall_btn = Button(SpriteAnimation(SpriteProvider.get("Arrows.png"), [1, 1], [64, 64], (228, int(599/2) + 1)), on_click=lambda: self.display_next_challenge())
		self.prev_chall_btn.get_spritesheet().set_animation_row(1)

		self.prev_chall_btn.on("mouse_enter", lambda: C.glitch())
		self.prev_chall_btn.on("mouse_leave", lambda: C.unglitch())
		self.next_chall_btn.on("mouse_enter", lambda: C.glitch())
		self.next_chall_btn.on("mouse_leave", lambda: C.unglitch())
		self.start_chall_btn.on("mouse_enter", lambda: C.glitch())
		self.start_chall_btn.on("mouse_leave", lambda: C.unglitch())

		# Create name input
		font_settings = FontSettings("resources/fonts/Code.ttf", 65, ColorProvider.get('fg'))
		self.username_prompt = TextDisplay(font_settings, content="Username:").set_max_width(C.DISPLAY_SIZE[0]).set_anchor("center").set_relative_pos((0.5, 0.5))
		self.username_input = TextArea(font_settings).set_max_width(C.DISPLAY_SIZE[0]).set_anchor("center").set_relative_pos((0.5, 0.5))
		self.username_input.move((0, 1.5 * self.username_prompt.height))
		self.username_input.on("type", lambda: self.add_element(self.start_chall_btn, True) if len(self.username_input.get_content()) >= 5 else self.rm_element(self.start_chall_btn))
		self.username_input.on("type", lambda: self.username_input.set_content(self.username_input.get_content()[:-1]) if len(
			self.username_input.get_content()) >= 16 else None)
		self.username_input.on("erase", lambda: self.rm_element(self.start_chall_btn) if not 15 >= len(self.username_input.get_content()) >= 5 else self.add_element(self.start_chall_btn, True))

		# Place challenge controls
		self.prev_chall_btn.set_anchor("center").set_relative_height(0.07).set_relative_pos((0, 0.5)).move((self.prev_chall_btn.width / 2 + self.CONTROL_MARGIN, 0))
		self.next_chall_btn.set_anchor("center").set_relative_height(0.07).set_relative_pos((1, 0.5)).move((-self.prev_chall_btn.width / 2 - self.CONTROL_MARGIN, 0))

	def on_set_active(self):
		self.display_current_challenge()

	def display_prev_challenge(self):
		self.current_challenge = (self.current_challenge - 1) % (challenge_manager.get_challenge_count() + 1)
		self.display_current_challenge()

	def display_next_challenge(self):
		self.current_challenge = (self.current_challenge + 1) % (challenge_manager.get_challenge_count() + 1)
		self.display_current_challenge()

	def display_current_challenge(self):
		self.get_elements().clear()
		self.add_element(self.prev_chall_btn)
		self.add_element(self.next_chall_btn)
		if challenge_manager.get_challenge_count() <= self.current_challenge:
			self.add_element(self.honeypot_logo)
			self.add_element(self.discord_qr_code)
			self.add_element(self.insta_qr_code)
		else:
			chall = challenge_manager.get_challenge(self.current_challenge)
			self.add_element(self.start_chall_btn)
			self.add_elements(chall.create_chall_display_elements_and_lb())
			self.start_chall_btn.set_click_callback(self.display_nickname_input_screen)

	def display_nickname_input_screen(self):
		chall = challenge_manager.get_challenge(self.current_challenge)

		self.get_elements().clear()

		self.add_element(self.username_prompt)
		self.add_element(self.username_input)
		self.add_elements(chall.create_chall_display_elements())

		self.start_chall_btn.set_click_callback(self.start_challenge)

	def start_challenge(self):
		if self.username_input.get_content() != "":
			self.current_player = self.username_input.get_content()
			self.username_input.set_content("")

		self.get_elements().clear()

		chall = challenge_manager.get_challenge(self.current_challenge)
		chall.reset_challenge()
		self.add_elements(chall.create_chall_session_elements())

	def end_challenge(self):
		chall = challenge_manager.get_challenge(self.current_challenge)
		result = chall.get_session_result()
		improved, rank = chall.submit_score(result)

		self.get_elements().clear()
		self.add_elements(chall.create_result_display_elements(result, improved, result if improved else chall.leaderboard.get_prev_entry(self.current_player).get_score(), rank))

