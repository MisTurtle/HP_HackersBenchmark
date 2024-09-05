import math
import random

import pygame
from abc import ABC, abstractmethod
from typing import Literal, Union, Callable, Any

from pygame import Rect

from elements.Attributes import Animation, PulseSettings
from providers import ColorProvider
from utils import C


ClickCallback = Callable[[], Any]
TypingCallback = Callable[[str], Any]


class SceneElement(pygame.Rect, ABC):

	WRAP_X = 0b01
	WRAP_Y = 0b10
	WRAP_BOTH = WRAP_X | WRAP_Y
	WRAP_NONE = 0b00

	SHAKE_SMOOTH_IN_OUT = 0
	SHAKE_SMOOTH_IN = 1
	SHAKE_INSTANT = 2

	@staticmethod
	def relative_to_absolute(rel: float, holder: float) -> float:
		return rel * holder

	def __init__(self, width: int, height: int, **kwargs):
		super().__init__((0, 0), (0, 0))

		self.holder = None
		self.listeners = {"create": [], "resize": [], "move": []}
		self.width, self.height = width, height
		self.prev_surface_size = 0, 0
		self.__original_size = self.width, self.height

		self.__anchor = "center"
		self.__animations: dict[str, Animation] = {}
		self.__zoom = 1, 1
		self.__shake_force, self.__shake_return_pos, self.__shake_mode = 0, (0, 0), self.SHAKE_SMOOTH_IN_OUT

		x = kwargs.get("x", self.relative_to_absolute(kwargs.get("relx", 0), C.DISPLAY_RECT.width))
		y = kwargs.get("y", self.relative_to_absolute(kwargs.get("rely", 0), C.DISPLAY_RECT.height))
		setattr(self, self.__anchor, (x, y))
		self.on_create()

	def on_create(self):
		pass

	def clear(self, event: str):
		self.listeners[event] = []

	def on(self, event: str, callback: Callable[['SceneElement'], Any]):
		if event not in self.listeners:
			self.listeners[event] = [callback]
		else:
			self.listeners[event].append(callback)

	def call(self, event: str):
		if event not in self.listeners:
			return
		for callback in self.listeners[event]:
			callback()

	def lock_pos(self, operation: Callable[[], None]):
		pos = getattr(self, self.__anchor)
		operation()
		setattr(self, self.__anchor, pos)

	def set_holder(self, holder: Union['Rect', None]) -> 'SceneElement':
		if holder is None:
			holder = C.DISPLAY_RECT
		self.holder = holder
		return self

	def get_holder(self) -> Union['Rect', None]:
		return self.holder or C.DISPLAY_RECT

	def set_original_size(self, size: tuple[int, int]):
		zoom = self.get_zoom()
		self.size = size
		self.__original_size = size
		self.set_zoom(zoom)
		self.call("resize")

	def add_animation(self, name: str, anim: Animation) -> 'SceneElement':
		self.__animations[name] = anim
		return self

	def rm_animation(self, name: str) -> 'SceneElement':
		del self.__animations[name]
		return self

	def get_animation(self, name: str) -> Union[Animation, None]:
		return self.__animations.get(name, None)

	def set_anchor(self, anchor: Literal['center', 'topleft', 'midtop', 'topright', 'midleft', 'midright', 'bottomleft', 'midbottom', 'bottomright']) -> 'SceneElement':
		setattr(self, anchor, getattr(self, self.__anchor))  # Refresh position
		self.__anchor = anchor
		self.call("move")
		return self

	def set_position(self, pos: tuple[float, float]) -> 'SceneElement':
		setattr(self, self.__anchor, pos)
		self.call("move")
		return self

	def get_position(self, holder: Union[pygame.Rect, None] = None) -> tuple[float, float]:
		holder = holder or self.get_holder()
		anchor_pos = getattr(self, self.__anchor)
		return anchor_pos[0] - holder.left, anchor_pos[1] - holder.top

	def set_relative_width(self, relw: float, keep_ratio: bool = True, holder: Union[pygame.Rect, None] = None) -> 'SceneElement':
		holder = holder or self.get_holder()

		def _():
			old, self.width = self.width, int(self.relative_to_absolute(relw, holder.width))
			if keep_ratio and old != 0:
				self.height *= self.width / old

		self.lock_pos(_)
		self.call("resize")
		return self

	def set_relative_height(self, relh: float, keep_ratio: bool = True, holder: Union[pygame.Rect, None] = None) -> 'SceneElement':
		holder = holder or self.get_holder()

		def _():
			old, self.height = self.height, int(self.relative_to_absolute(relh, holder.height))
			if keep_ratio and old != 0:
				self.width *= self.height / old

		self.lock_pos(_)
		self.call("resize")
		return self

	def set_relative_pos(self, relpos: tuple[float, float], holder: Union[pygame.Rect, None] = None) -> 'SceneElement':
		holder = holder or self.get_holder()
		setattr(self, self.__anchor, (holder.left + self.relative_to_absolute(relpos[0], holder.width), holder.top + self.relative_to_absolute(relpos[1], holder.height)))
		self.call("move")
		return self

	def set_absolute_pos(self, pos: tuple[float, float], holder: Union[pygame.Rect, None] = None) -> 'SceneElement':
		holder = holder or self.get_holder()
		setattr(self, self.__anchor, (holder.left + pos[0], holder.top + pos[1]))
		self.call("move")
		return self

	def set_zoom(self, scale: tuple[float, float]) -> 'SceneElement':
		def _():
			self.width, self.height = int(self.__original_size[0] * scale[0]), int(self.__original_size[1] * scale[1])

		self.lock_pos(_)
		self.call("resize")
		return self

	def zoom_by(self, factor: tuple[float, float]) -> 'SceneElement':
		def _():
			self.width *= factor[0]
			self.height *= factor[1]

		self.lock_pos(_)
		self.call("resize")
		return self

	def get_zoom(self) -> tuple[float, float]:
		if self.__original_size[0] == 0 or self.__original_size[1] == 0:
			return 1, 1
		return self.width / self.__original_size[0], self.height / self.__original_size[1]

	def shake(self, amplitude: float, duration: float, mode: SHAKE_SMOOTH_IN_OUT, then: Union[Callable[[], None], None] = None):
		assert duration > 0
		anim = self.get_animation("shake")
		if anim is None:
			anim = Animation(duration)
			self.add_animation("shake", anim)
			self.__shake_return_pos = self.get_position()
		else:
			anim.reset().set_speed(anim.get_duration() / duration)

		self.__shake_force = amplitude
		self.__shake_mode = mode

		def end_behavior(_):
			anim.pause()
			self.set_absolute_pos(self.__shake_return_pos)
			if then is not None:
				then()
		anim.set_end_behavior(end_behavior)
		anim.start()

	def stop_shaking(self):
		anim = self.get_animation("shake")
		if anim is None:
			return
		anim.reset()

	def move(self, delta: tuple[float, float], wrap: int = WRAP_NONE, holder: Union[pygame.Rect, None] = None) -> int:
		holder = holder or self.get_holder()
		self.move_ip(delta)
		wrapped = self.WRAP_NONE
		if wrap & self.WRAP_X:
			if holder.left > self.right:
				self.left = holder.right if delta[0] < 0 else holder.left - self.width
				wrapped |= self.WRAP_X
			elif holder.right < self.left:
				self.right = holder.left if delta[0] > 0 else holder.right + self.width
				wrapped |= self.WRAP_X
		if wrap & self.WRAP_Y:
			if holder.top > self.bottom:
				self.top = holder.bottom if delta[1] < 0 else holder.top - self.height
				wrapped |= self.WRAP_Y
			elif holder.bottom < self.top:
				self.bottom = holder.top if delta[1] > 0 else holder.bottom + self.height
				wrapped |= self.WRAP_Y
		self.call("move")
		return wrapped

	def get_drawing_position(self, surface_id: int) -> tuple[float, float]:
		return self.left, self.top

	@abstractmethod
	def render(self) -> list[pygame.Surface]:
		pass

	def tick(self, dt: float):
		for animation in self.__animations.values():
			animation.tick(dt)
		shake_anim = self.get_animation("shake")
		if shake_anim is not None and shake_anim.is_running():
			c = 1
			match self.__shake_mode:
				case self.SHAKE_SMOOTH_IN_OUT:
					c = math.sin(shake_anim.get_progress_percent() * math.pi)
				case self.SHAKE_SMOOTH_IN:
					c = math.sin(min(1., shake_anim.get_progress_percent() * 1.5) * math.pi / 2)
			og = self.__shake_return_pos
			self.set_absolute_pos((og[0] + (random.random() - 0.5) * self.__shake_force * c, og[1] + (random.random() - 0.5) * self.__shake_force * c))
		self.call("tick")

	def draw(self, where: pygame.Surface):
		i = 0
		for surface in self.render():
			scale = self.get_zoom()
			if scale[0] != 1. or scale[1] != 1.:
				surface = pygame.transform.smoothscale_by(surface, scale)
			where.blit(surface, self.get_drawing_position(i))
			self.prev_surface_size = surface.get_size()
			i += 1


class Hoverable(SceneElement, ABC):

	# Properties
	__enabled = True
	__draggable = False
	__one_click_per_frame = False
	__last_clicked_frame = 0

	# State
	__hovered = False
	__clicked = False
	__dragging = False
	__prev_mouse_pos = 0, 0

	def set_enabled(self, enabled: bool = True) -> 'Hoverable':
		self.__enabled = enabled
		if self.is_hovered():
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
		return self

	def set_one_click_per_frame(self, val: bool):
		self.__one_click_per_frame = val

	def is_one_click_per_frame(self) -> bool:
		return self.__one_click_per_frame

	def is_enabled(self) -> bool:
		return self.__enabled

	def set_draggable(self, draggable: bool = True) -> 'Hoverable':
		self.__draggable = draggable
		if not draggable:
			self.__dragging = False
		elif "drag" not in self.listeners:
			self.listeners["drag"] = []
		return self

	def is_draggable(self) -> bool:
		return self.__draggable and self.is_enabled()

	def is_being_dragged(self) -> bool:
		return self.__dragging and self.__enabled

	def is_hovered(self) -> bool:
		return self.__hovered

	def set_hovered(self, hovered: bool):
		self.__hovered = hovered

	def is_clicked(self) -> bool:
		return self.__clicked

	# Mouse event handling
	def on_mouse_enter(self):
		if not self.is_enabled():
			return
		self.__hovered = True
		self.call("mouse_enter")
		if self.is_draggable():
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)

	def on_mouse_leave(self):
		self.__hovered = False
		self.__clicked = False
		self.call("mouse_leave")
		if self.__draggable:
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

	def on_mouse_click(self, pos: tuple[float, float], button: int):
		"""
		This is called even if the element is not hovered
		"""
		if not self.is_hovered() or button != pygame.BUTTON_LEFT or not self.is_enabled():
			return
		if self.is_one_click_per_frame() and self.__last_clicked_frame == C.FRAME_ID:
			return
		self.call("click")
		self.__clicked = True
		self.__prev_mouse_pos = pos
		self.__last_clicked_frame = C.FRAME_ID

	def on_mouse_move(self, pos: tuple[int, int]):
		if not self.is_draggable() or not self.is_clicked():
			return
		pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
		self.__dragging = True
		self.move((pos[0] - self.__prev_mouse_pos[0], pos[1] - self.__prev_mouse_pos[1]))
		self.call("drag")
		self.__prev_mouse_pos = pos

	def on_mouse_release(self, button: int):
		if not self.is_clicked() or button != pygame.BUTTON_LEFT:
			return
		self.__clicked = False
		self.__dragging = False



class Typable(SceneElement, ABC):

	__typing_handler: TypingCallback = lambda _: None

	@abstractmethod
	def on_type(self, letter: str):
		pass


class Pulsing(SceneElement, ABC):

	pulse_settings: PulseSettings = PulseSettings(1, 0.05, (1, 1))

	def on_create(self):
		self.add_animation("pulse", Animation(self.pulse_settings.get_period()).set_end_behavior(Animation.REWIND_ON_END).start())

	def set_pulse_settings(self, settings: PulseSettings) -> 'Pulsing':
		self.rm_animation("pulse")
		self.pulse_settings = settings
		self.add_animation("pulse", Animation(self.pulse_settings.get_period()).set_end_behavior(Animation.REWIND_ON_END).start())
		return self

	def get_pulse_settings(self) -> PulseSettings:
		return self.pulse_settings

	def set_relative_width(self, relw: float, keep_ratio: bool = True, holder: Union[pygame.Rect, None] = None) -> 'SceneElement':
		super().set_relative_width(relw, keep_ratio, holder)
		self.pulse_settings.set_base(self.get_zoom())
		return self

	def set_relative_height(self, relh: float, keep_ratio: bool = True, holder: Union[pygame.Rect, None] = None) -> 'SceneElement':
		super().set_relative_height(relh, keep_ratio, holder)
		self.pulse_settings.set_base(self.get_zoom())
		return self

	def tick(self, dt: float):
		super().tick(dt)
		self.set_zoom(self.pulse_settings.compute(self.get_animation("pulse").get_progress()))


class ElementGroup(Hoverable, SceneElement):

	_elements = []

	@staticmethod
	def compute_size_from_components(components: list[SceneElement]):
		"""
		:param components: List of components
		:return: Left, Top, Right, Bottom, Center X, Center Y
		"""
		left, top, right, bot = None, None, None, None
		for component in components:
			if left is None or component.left < left:
				left = component.left
			if right is None or component.right > right:
				right = component.right
			if top is None or component.top < top:
				top = component.top
			if bot is None or component.bottom > bot:
				bot = component.bottom
		return left, top, right, bot, int((right - left) / 2), int((bot - top) / 2)

	def __init__(self, elements: list[SceneElement], **kwargs):
		SceneElement.__init__(self, 0, 0, **kwargs)
		self._elements = elements
		self._background_color = kwargs.get("bg", None)
		for el in self._elements:
			el.set_holder(self)

	def get_background_color(self) -> Union[pygame.Color, None]:
		return self._background_color

	def set_background_color(self, color: Union[pygame.Color, None]) -> 'ElementGroup':
		self._background_color = color
		return self

	def add_element(self, el: SceneElement, add_to_scene: bool) -> 'ElementGroup':
		from scene import scene_manager

		self._elements.append(el)
		if add_to_scene:
			scene_manager.get_current_scene().add_element(el)
		el.set_holder(self)
		return self

	def rm_element(self, el: SceneElement, rm_from_scene: bool) -> 'ElementGroup':
		from scene import scene_manager

		self._elements.remove(el)
		if rm_from_scene:
			scene_manager.get_current_scene().rm_element(el)
		el.set_holder(None)
		return self

	def clear_elements(self, rm_from_scene: bool = True):
		from scene import scene_manager

		for el in self.get_elements():
			if rm_from_scene:
				scene_manager.get_current_scene().rm_element(el)
			el.set_holder(None)
		self._elements.clear()

	def set_relative_pos(self, relpos: tuple[float, float], holder: Union[pygame.Rect, None] = None) -> 'SceneElement':
		old_pos = self.get_position(C.DISPLAY_RECT)
		super().set_relative_pos(relpos, holder)
		new_pos = self.get_position(C.DISPLAY_RECT)
		delta = new_pos[0] - old_pos[0], new_pos[1] - old_pos[1]
		for el in self.get_elements():
			el.move(delta)
		return self

	def move(self, delta: tuple[float, float], wrap: int = SceneElement.WRAP_NONE, holder: Union[pygame.Rect, None] = None) -> int:
		w = super().move(delta, wrap, holder)
		for el in self.get_elements():
			el.move(delta, wrap, self)
		return w

	def tick(self, dt: float):
		super().tick(dt)

	def render(self) -> list[Union[pygame.Surface, list[pygame.Surface]]]:
		if self.get_background_color() is None:
			return []
		s = pygame.Surface(self.size)
		s.fill(ColorProvider.get('bg'))
		pygame.draw.rect(s, self._background_color, s.get_rect(), 5)
		return [s]

	def get_elements(self):
		return self._elements
