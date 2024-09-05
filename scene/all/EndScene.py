import pygame

from elements.Attributes import FontSettings, PulseSettings, SpriteAnimation
from elements.Elements import PulsingText, TextDisplay, Sprite
from elements.Types import ElementGroup
from game import challenge_manager
from providers import ColorProvider, SpriteProvider
from scene import Scene
from utils import C


class EndScene(Scene):

	def __init__(self):
		super().__init__()

		logo = Sprite(
			SpriteAnimation(SpriteProvider.get("HoneyPot_Logo_NOBG_Centered.png"), [1], [60], (1051, 1138))
		).set_relative_height(0.33).set_anchor("center").set_relative_pos((0.5, 0.3))
		self.add_element(logo)

		qr_code = Sprite(
			SpriteAnimation(SpriteProvider.get("HoneyPot_QR_Discord.png"), [1], [60], (485, 485))
		).set_relative_height(0.33).set_anchor("midright").set_relative_pos((0.9, 0.3))
		self.add_element(qr_code)
		# Logo goes till 0.3 + 0.33/2 = 0.3 + 0.165 = 0.435

	def on_set_active(self):
		C.unglitch()
