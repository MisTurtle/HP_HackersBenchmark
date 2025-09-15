import os
from typing import Optional
from hb_screens.challenges.ConflictsSolverChallenge import ConflictsSolverChallenge
from hb_screens.challenges.TimeMasterChallenge import TimeMasterChallenge
from hb_screens.challenges.BugHunterChallenge import BugHunterChallenge
from hb_screens.challenges.MindTripTimeChallenge import MindTripTimeChallenge
from hb_screens.challenges.TypingFrenzyChallenge import TypingFrenzyChallenge
from hb_screens.screen_result import ScreenAction
from hb_types.scenes import Scene
from hb_types.widgets import BinaryDropText, ImageWidget, TextButton, TextInputWidget, TextWidget
from hb_utils.factories import ColorProvider, FontProvider, SpriteProvider
from hb_utils.info import PlayerInfo
from hb_utils.leaderboard import Leaderboard, get_best_average_placement
from hb_utils.maths import auto_width, ease_in_out

class WelcomeScreen(Scene):

    def __init__(self, player_info: Optional[PlayerInfo]):
        super().__init__(player_info, ColorProvider.get('bg'))

        for _ in range(50):
            self.add_widget(BinaryDropText())
        self.main_logo = self.add_widget(self._create_main_logo())
        self.start_button = self.add_widget(self._create_start_button())

        leaderboards = [
            BugHunterChallenge.get_leaderboard(),
            MindTripTimeChallenge.get_leaderboard(),
            TimeMasterChallenge.get_leaderboard(),
            TypingFrenzyChallenge.get_leaderboard(),
            ConflictsSolverChallenge.get_leaderboard()
        ]
        best_players = get_best_average_placement(leaderboards)
        if len(best_players) > 0:
            template = "#{i:<2} {name:<20} - Rang: {placement:.2f}"
            best = "\n".join(template.format(i=i + 1, name=best_players[i][0], placement=best_players[i][1]) for i in range(min(len(best_players), 3)))
            if self.player_info is not None:
                current_player_rank = next((i for i in range(len(best_players)) if best_players[i][0].lower() == self.player_info.username.lower()), None)
                if current_player_rank is not None and current_player_rank >= 3:
                    best += "\n" + "-" * 36 + "\n" + template.format(i=current_player_rank + 1, name=self.player_info.username, placement=best_players[current_player_rank][1])
            self.best_player = TextWidget("Top 3 Hackers\n" + best, font=FontProvider.get(("JACK.TTF", 42)), color=ColorProvider.get('fg'), align='center', rel_x=0.5, rel_y=0.75, rel_width=0.8, rel_height=0.4)
            self.best_player.zoom.animate(start=0, end=1, duration=0.5, easing=ease_in_out)
            self.add_widget(self.best_player)
        
    def _create_main_logo(self) -> ImageWidget:
        image = SpriteProvider.get('HoneyPot_Logo.png')
        rel_height = 0.33
        rel_width = auto_width(rel_height, image.get_size(), self.get_rect().size)
        w = ImageWidget(image, rel_x=0.5, rel_y=0.3, rel_height=rel_height, rel_width=rel_width)
        zoom_size = 1.05
        w.rel_width.animate(w.rel_width.value, w.rel_width.value * zoom_size, 0.5, True, easing=ease_in_out)
        w.rel_height.animate(w.rel_height.value, w.rel_height.value * zoom_size, 0.5, True, easing=ease_in_out)
        w.zoom.animate(0, 1, 0.5, easing=ease_in_out)
        return w
    
    def _create_start_button(self):
        w = TextButton( text="Hacker", font_name='Camcode.ttf', callback=self.start_callback, bg_color=ColorProvider.get('bg'), rel_x=0.5, rel_y=0.9, rel_height=0.1, rel_width=0 )
        w.color.animate(start=ColorProvider.get('fg'), end=ColorProvider.get('fg2'), duration=1, loop=True, easing=ease_in_out)
        w.zoom.animate(0, 1, 0.5, easing=ease_in_out)
        return w

    def start_callback(self):
        self._action = ScreenAction.LOAD_NEXT
        self.close()
        self.notify()

