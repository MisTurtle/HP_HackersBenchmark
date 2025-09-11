from typing import List, Optional, Union
import pygame
from abc import ABC, abstractmethod

from hb_screens.screen_result import ScreenAction
from hb_types.observers import SimpleSubject
from hb_types.widgets import Widget
from hb_utils.animations import AnimatedValue
from hb_utils.info import PlayerInfo
from hb_utils.maths import ease_in_out

class Scene(SimpleSubject, ABC):

    MAX_SCENE_TRANSITION_DURATION = 3

    _action: Union[None, ScreenAction] = ScreenAction.QUIT_PROGRAM

    def __init__(self, player_info: PlayerInfo, background: pygame.color.Color = (0, 0, 0), screen_rect: Optional[pygame.Rect] = None, widgets: Optional[List[Widget]] = None):
        super().__init__()
        self.bg_color = AnimatedValue(background)
        self._player_info = player_info
        self._screen_rect = screen_rect if screen_rect is not None else pygame.display.get_surface().get_rect()
        self._widgets = widgets if widgets is not None else []
        self._closed = False

    @property
    def player_info(self) -> PlayerInfo:
        return self._player_info

    @property
    def action(self):
        return self._action

    def get_rect(self) -> pygame.Rect:
        return self._screen_rect
    
    def add_widget(self, w: Widget):
        if w not in self._widgets:
            self._widgets.append(w)
        return w
    
    def remove_widget(self, w: Widget):
        if w in self._widgets:
            self._widgets.remove(w)
        return w
    
    def clear_widgets(self):
        self._widgets.clear()
    
    def update(self, dt):
        self.bg_color.update(dt)
        for w in self._widgets:
            w.update(dt)

    def draw(self, surface: pygame.Surface):
        """
        Draw the scene in its current state onto the surface
        """
        for w in self._widgets:
            w.draw(surface)
    
    def handle_event(self, event: pygame.event.Event):
        for w in self._widgets:
            w.handle_event(event)
    
    def close(self):
        for w in self._widgets:
            w.zoom.animate(1, 0, self.MAX_SCENE_TRANSITION_DURATION / 2, easing=ease_in_out)
