from hb_screens.challenge_screen import ChallengeScreen
from hb_types.game_widgets import LatencyTimeWidget, TimeMasterWidget
from hb_utils.factories import ColorProvider
from hb_utils.leaderboard import Leaderboard


class TimeMasterChallenge(ChallengeScreen):

    @staticmethod
    def get_leaderboard() -> Leaderboard:
        return Leaderboard("Time Master", False)

    def __init__(self, player_info):
        super().__init__("Time Master", "Pas le temps pour les tests, il faut faire la montée en prod ASAP! Tu sais que le timing est la clé de la réussite.\n\nClique sur le bouton de mise en production, puis valide les changements 15 secondes après.", True, player_info)
    
    def prepare_game(self):
        super().prepare_game()
        self.game_widget = TimeMasterWidget(
            border_color=ColorProvider.get('fg'),
            rel_x=0.5, rel_y=0.5, rel_width=0.8, rel_height=0.65,
            on_complete=self.display_results
        )

    def _internal_start_game(self):
        self.add_widget(self.game_widget)

    def display_results(self):
        super().display_results()
        self.challenge_result.text = ("%.3fs / 15s" % self.game_widget.result_time) + "\n" + self.challenge_result.text

    def _get_result(self):
        return abs(15 - self.game_widget.result_time)

    def _format_result_to_display(self, result):
        return "±%.3fs (%.2f%%)" % (result, 100 * (1 - result / 15))
    