from typing import Optional
import pygame
from hb_screens.screen_result import ScreenAction
from hb_types.scenes import Scene
from hb_types.widgets import BinaryDropText, ImageWidget, TextButton, TextInputWidget, TextWidget
from hb_utils.factories import ColorProvider, FontProvider, SpriteProvider
from hb_utils.info import PlayerInfo
from hb_utils.maths import auto_width, ease_in_out

class SynopsisScreen(Scene):

    def __init__(self, player_info: Optional[PlayerInfo]):
        super().__init__(player_info, ColorProvider.get('bg_dark'))
        self.main_text = TextWidget(
            "Une faille a été détectée dans notre Honeypot, et un hacker en a profité pour infiltrer nos serveurs. Tu es le seul à avoir les capacités pour le repousser et remettre nos barrières de sécurité en place.\n\nSous quel nom deviendras-tu célèbre ?",
            FontProvider.get(('JACK.TTF', 32)),
            ColorProvider.get('fg2'),
            align='center',
            reveal_letters=True,
            start_color=ColorProvider.get('bg_dark'),
            line_height_multiplier=1.2,
            rel_x=0.5, rel_y=0.4, rel_width=0.5, rel_height=0.1
        )
        self.add_widget(self.main_text)
        
        self.cancel_button = self._create_cancel_button()
        self.start_button = self._create_start_button()
        self.name_input = self._create_name_input()

        self.main_text.after(lambda: (self.add_widget(self.cancel_button), self.add_widget(self.name_input)))
    
    def _create_cancel_button(self):
        w = TextButton( text="Retourner se coucher", font_name='JACK.TTF', callback=self.cancel_callback, rel_x=0.25, rel_y=0.9, rel_height=0.06, rel_width=0 )
        w.color.animate(start=ColorProvider.get('error'), end=ColorProvider.get('error2'), duration=1, loop=True, easing=ease_in_out)
        w.zoom.animate(start=0, end=1, duration=0.3, easing=ease_in_out)
        return w
    
    def _create_start_button(self):
        w = TextButton( text="Défendre le serveur", font_name='JACK.TTF', callback=self.start_callback, rel_x=0.75, rel_y=0.9, rel_height=0.06, rel_width=0 )
        w.color.animate(start=ColorProvider.get('success'), end=ColorProvider.get('success2'), duration=1, loop=True, easing=ease_in_out)
        w.zoom.animate(start=0, end=1, duration=0.3, easing=ease_in_out)
        return w
    
    def _create_name_input(self):
        w = TextInputWidget(
            text="", font=FontProvider.get(('JACK.TTF', 48)), color=ColorProvider.get('fg'), cursor_transparent_color=ColorProvider.get('bg_dark'), align='center', min_length=3, max_length=20,
            rel_x=0.5, rel_y=0.7, rel_height=0.1
        )
        def _():
            if len(w.text) == 0:
                self.start_button.zoom.animate(start=1, end=0, duration=0.3, after=lambda: self.remove_widget(self.start_button), easing=ease_in_out)
            elif self.start_button.zoom.value != 1:
                self.start_button.zoom.animate(start=self.start_button.zoom.value, end=1, duration=0.3, easing=ease_in_out)
                self.add_widget(self.start_button)
        w.on_change(_)
        w.on_submit(self.start_callback)
        return w
        
    def cancel_callback(self):
        self._action = ScreenAction.LOAD_PREVIOUS
        self.close()
        self.notify()

    def start_callback(self):
        if len(self.name_input.text) == 0:
            return
        self._player_info = PlayerInfo(self.name_input.text)
        self._action = ScreenAction.LOAD_NEXT
        self.close()
        self.notify()

