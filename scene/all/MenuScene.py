from elements.Attributes import SpriteAnimation, PulseSettings, FontSettings
from elements.Elements import Button, BinaryDropText, PulsingImage, PulsingText, TextDisplay
from elements.Types import ElementGroup
from providers import SpriteProvider, ColorProvider
from scene import Scene, scene_manager
from utils import C


class MenuScene(Scene):

	def __init__(self):
		super().__init__()

		for i in range(50):
			self.add_element(BinaryDropText(
					FontSettings("resources/fonts/Code.ttf", 30, ColorProvider.get("fg"))
				))

		logo = PulsingImage(
			SpriteAnimation(SpriteProvider.get("HoneyPot_Logo_NOBG_Centered.png"), [1], [60], (1051, 1138))
		).set_pulse_settings(PulseSettings(period=0.83, amplitude=0.05, base=(1, 1))).set_relative_height(0.27).set_anchor("center").set_relative_pos((0.5, 0.3))
		self.add_element(logo)

		start_btn = Button(
			SpriteAnimation(SpriteProvider.get("Btn_StartGame.png"), [20], [0.05], (600, 250)).set_mode(SpriteAnimation.MODE_CIRCULAR),
			on_click=lambda: scene_manager.set_active_scene(scene_manager.GAME_SCENE),
			relx=0.5, rely=0.7
		).set_relative_height(0.15)
		self.add_element(start_btn)
		start_btn.on("mouse_enter", lambda: C.glitch())
		start_btn.on("mouse_leave", lambda: C.unglitch())
