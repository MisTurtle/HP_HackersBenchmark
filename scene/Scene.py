from typing import Union

import pygame
from abc import ABC
from providers import ColorProvider
from elements.Types import SceneElement, Hoverable, Typable, ElementGroup


class Scene(ABC):

	def __init__(self):
		self._elements: list[SceneElement] = []
		self._hovered_element: Union[Hoverable, None] = None

	def add_element(self, element: SceneElement, only_if_absent: bool = False):
		if only_if_absent and element in self._elements:
			return
		self._elements.append(element)
		if isinstance(element, ElementGroup):
			for el in element.get_elements():
				self._elements.append(el)

	def add_elements(self, elements: list[SceneElement]):
		for e in elements:
			self.add_element(e)

	def rm_element(self, element: SceneElement):
		if element not in self._elements:
			return
		self._elements.remove(element)
		if isinstance(element, ElementGroup):
			for el in element.get_elements():
				self._elements.remove(el)

	def get_elements(self) -> list[SceneElement]:
		return self._elements

	def update(self, dt: float):
		for element in self._elements:
			element.tick(dt)

	def draw(self, where: pygame.Surface):
		where.fill(ColorProvider.get('bg'))
		for element in self._elements:
			element.draw(where)

	def on_mouse_enter_actions(self):
		pass

	def on_mouse_leave_actions(self):
		pass

	def on_click_actions(self):
		pass

	def set_cursor(self, cursor_pos: tuple[int, int]):
		if self._hovered_element is not None and self._hovered_element.is_being_dragged():
			self._hovered_element.on_mouse_move(cursor_pos)
			return
		for element in reversed(self._elements):
			if not isinstance(element, Hoverable):
				continue
			element.on_mouse_move(cursor_pos)
			if not element.collidepoint(cursor_pos):
				continue
			if element.is_hovered() and self._hovered_element == element:
				return
			if self._hovered_element is not None:
				self._hovered_element.on_mouse_leave()

			self._hovered_element = element
			element.on_mouse_enter()
			return

		if self._hovered_element is not None:
			self._hovered_element.on_mouse_leave()
			self._hovered_element = None

	def handle_click(self, pos: tuple[int, int], btn: int):
		for element in reversed(self._elements):
			if isinstance(element, Hoverable):
				element.on_mouse_click(pos, btn)

	def handle_release(self, btn: int):
		if self._hovered_element is not None:
			self._hovered_element.on_mouse_release(btn)

	def on_set_active(self):
		pass

	def on_set_inactive(self):
		if self._hovered_element is not None:
			self._hovered_element.on_mouse_leave()

	def type(self, letter: str):
		if letter == '\r':
			letter = '\n'
		for element in self._elements:
			if isinstance(element, Typable):
				element.on_type(letter)
