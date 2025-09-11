from abc import ABC, abstractmethod
from typing import Optional
import pygame
from hb_screens.screen_result import ScreenAction
from hb_types.scenes import Scene
from hb_types.widgets import BinaryDropText, ImageWidget, TextButton, TextInputWidget, TextWidget
from hb_utils.factories import ColorProvider, FontProvider, SpriteProvider
from hb_utils.info import PlayerInfo
from hb_utils.leaderboard import Leaderboard, LeaderboardEntry
from hb_utils.maths import auto_width, ease_in_out

class ChallengeScreen(Scene, ABC):

    @staticmethod
    def get_leaderboard() -> Leaderboard:
        pass

    def __init__(self, challenge_name, challenge_description, lower_is_better: bool, player_info: Optional[PlayerInfo]):
        super().__init__(player_info, ColorProvider.get('bg_dark'))
        self._started = False
        self._leaderboard = Leaderboard(challenge_name, descending=not lower_is_better)

        self.challenge_title = TextWidget(challenge_name, font=FontProvider.get(('JACK.TTF', 64)), color=ColorProvider.get('fg'), align='center', rel_x=0.5, rel_y=0.1, rel_width=0.5, rel_height=0.1)
        self.challenge_title.color.animate(ColorProvider.get('bg_dark'), ColorProvider.get('fg'), 0.5, easing=ease_in_out)
        self.add_widget(self.challenge_title)
        
        self.challenge_description = TextWidget(
            challenge_description,
            FontProvider.get(('JACK.TTF', 32)),
            ColorProvider.get('fg2'),
            align='center',
            reveal_letters=True,
            start_color=ColorProvider.get('bg_dark'),
            line_height_multiplier=1.2,
            rel_x=0.5, rel_y=0.4, rel_width=0.5, rel_height=0.1
        )
        self.add_widget(self.challenge_description)

        self.start_button = TextButton( text="Let's go", font_name='JACK.TTF', callback=self.prepare_game, rel_x=0.5, rel_y=0.9, rel_height=0.05, rel_width=0 )
        _ = lambda: self.start_button.color.animate(start=ColorProvider.get('fg'), end=ColorProvider.get('fg2'), duration=1, loop=True, easing=ease_in_out)
        self.start_button.color.animate(start=ColorProvider.get('bg_dark'), end=ColorProvider.get('fg'), after=_, duration=1, loop=False, easing=ease_in_out)
        self.add_widget(self.start_button)

        self.challenge_result = TextWidget("", font=FontProvider.get(("JACK.TTF", 64)), color=ColorProvider.get('fg2'), align='center', rel_x=0.5, rel_y=0.3, rel_width=0.8, rel_height=0.1)
        
        self.leaderboard_display = TextWidget("", font=FontProvider.get(("JACK.TTF", 42)), color=ColorProvider.get('fg2'), align='center', rel_x=0.5, rel_y=0.7, rel_width=0.8, rel_height=0.4)

        self.restart_button = TextButton( text="Réessayer", font_name='JACK.TTF', color=ColorProvider.get('fg'), callback=self.replay, rel_x=0.25, rel_y=0.9, rel_height=0.05, rel_width=0 )
        self.continue_button = TextButton( text="Continuer", font_name='JACK.TTF', color=ColorProvider.get('fg'), callback=self.continue_callback, rel_x=0.75, rel_y=0.9, rel_height=0.05, rel_width=0 )

    def prepare_game(self):
        for widget in self._widgets:
            if widget != self.challenge_title:
                widget.zoom.animate(widget.zoom.value, end=0, duration=0.5, after=lambda: self.start_game(), easing=ease_in_out)

    def start_game(self):
        if not self._started:
            for widget in self._widgets.copy():
                if widget.zoom.value < 0.5:
                    self.remove_widget(widget)
                    widget.zoom.value = 1
                    widget.zoom.animating = False

            self._internal_start_game()
            self._started = True

    @abstractmethod
    def _internal_start_game(self):
        pass
        
    def display_results(self):
        for widget in self._widgets.copy():
            if widget != self.challenge_title:
                self.remove_widget(widget)
        
        result = self._get_result()
        entry = LeaderboardEntry(self.player_info.username, result)
        self._leaderboard.add_score(entry)
        rank = self._leaderboard.get_rank(entry.get_name())

        self.challenge_result.text = self._format_result_to_display(result)
        self.add_widget(self.challenge_result)

        top = self._leaderboard.get_top(5)
        template = "#{rank:<4}{username:<20}-   {score}"
        lines = "\n".join(template.format(rank=i + 1, username=e.get_name(), score=self._format_result_to_display(e.get_score())) for i, e in enumerate(top))
        if rank > 5:
            lines += "\n" + ("-" * 24) + "\n" + template.format(rank=rank, username=entry.get_name(), score=self._format_result_to_display(entry.get_score()))
        self.leaderboard_display.text = lines
        self.add_widget(self.leaderboard_display)

        self.add_widget(self.restart_button)
        self.add_widget(self.continue_button)
 
    @abstractmethod
    def _get_result(self):
        pass
        
    @abstractmethod
    def _format_result_to_display(self, result):
        pass

    def replay(self):
        self._started = False
        self.prepare_game()
    
    def continue_callback(self):
        self._action = ScreenAction.LOAD_NEXT
        self.close()
        self.notify()
