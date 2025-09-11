import random
from hb_screens.challenge_screen import ChallengeScreen
from hb_types.game_widgets import BugHunterGameWidget, LatencyTimeWidget
from hb_types.widgets import GuidedTextInputWidget, Timer
from hb_utils.factories import ColorProvider, FontProvider, SpriteProvider
from hb_utils.leaderboard import Leaderboard


class TypingFrenzyChallenge(ChallengeScreen):

    ALL = [
        "[](){ rkhunter::scan() && backdoor::purge(*process); }();",
        "[](){ rkhunter::check(0) && rkhunter::disarm(*pid); }();",
        "[](){ net::cloak_traffic(443) && log::erase_all(); }();",
        "[](){ process::spoof(*pid) && process::hide_threads(); }();",
        "[](){ exploit::zero_day(*target)::deploy(\"reverse_shell\"); }();"
    ]

    @staticmethod
    def get_leaderboard() -> Leaderboard:
        return Leaderboard("Typing Frenzy", True)

    def __init__(self, player_info):
        super().__init__("Typing Frenzy", "Sans plus tarder, tu t'attelles à l'écriture d'un patch ! Tu n'as même pas eu le temps de boire ton café...\n\nRecopie l'extrait de code affiché à l'écran le plus vite possible !", False, player_info)

    def prepare_game(self):
        super().prepare_game()
        self.timer = Timer(
            font=FontProvider.get(('Camcode.ttf', 45)),
            color=ColorProvider.get('fg'),
            rel_x=0.5, rel_y=0.3, rel_width=0.8, rel_height=0.1,
            align='center'
        )
        self.game_widget = GuidedTextInputWidget(
            TypingFrenzyChallenge.ALL[random.randint(0, len(TypingFrenzyChallenge.ALL) - 1)],
            font=FontProvider.get(('JetBrainsMono-Medium.ttf', 28)),
            align="center",
            placeholder_color=ColorProvider.get('bg_dark_lighter'),
            rel_x=0.5, rel_y=0.5, rel_width=0.8, rel_height=0.1, 
            on_type=self.timer.start,
            on_complete=lambda: (self.timer.stop(), self.display_results())
        )

    def _internal_start_game(self):
        self.add_widget(self.game_widget)
        self.add_widget(self.timer)

    def _get_result(self):
        return 60 * len(self.game_widget.placeholder) / (5 * self.timer.get())

    def _format_result_to_display(self, result):
        return "%.2f WPS" % result
    