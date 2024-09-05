from typing import Union

from providers import ShaderProvider
from scene.Scene import Scene
from utils import Singleton, Provider


class SceneManager(Provider[int, Scene], metaclass=Singleton):

	MENU_SCENE = 0
	GAME_SCENE = 1
	END_SCENE = 2

	def __init__(self):
		super().__init__()
		self._current_scene: Union[Scene, None] = None
		self._previous_scene: Union[Scene, None] = None

	def get_current_scene(self) -> Union[Scene, None]:
		return self._current_scene

	def get_previous_scene(self) -> Union[Scene, None]:
		return self._previous_scene

	def set_active_scene(self, scene: Union[int, None]):
		self._previous_scene, self._current_scene = self._current_scene, self.get(scene)
		if self._previous_scene is not None:
			self._previous_scene.on_set_inactive()
		if self._current_scene is not None:
			self._current_scene.on_set_active()

	def set_cursor(self, pos: tuple[int, int]):
		if self._current_scene is None:
			return
		self._current_scene.set_cursor(pos)

	def handle_click(self, pos: tuple[int, int], btn: int):
		if self._current_scene is None:
			return
		self._current_scene.handle_click(pos, btn)

	def handle_release(self, btn: int):
		if self._current_scene is None:
			return
		self._current_scene.handle_release(btn)

	def type(self, letter: str):
		if self._current_scene is None:
			return
		self._current_scene.type(letter)

