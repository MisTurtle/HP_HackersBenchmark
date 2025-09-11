from hb_screens.challenge_screen import ChallengeScreen
from hb_types.game_widgets import BugHunterGameWidget, LatencyTimeWidget
from hb_utils.factories import ColorProvider, SpriteProvider
from hb_utils.leaderboard import Leaderboard


class BugHunterChallenge(ChallengeScreen):

    @staticmethod
    def get_leaderboard() -> Leaderboard:
        return Leaderboard("Bug Hunter", False)

    def __init__(self, player_info):
        super().__init__("Bug Hunter", "La situation est grave, il faut absolument réussir à régler cette faille !\n\nClique sur le bug 15 fois à la suite pour trouver l'origine du problème.", True, player_info)
    
    def prepare_game(self):
        super().prepare_game()
        self.game_widget = BugHunterGameWidget(SpriteProvider.get('AimBug.png'), n_targets=15, rel_x=0.5, rel_y=0.5, rel_width=0.75, rel_height=0.6, on_complete=self.display_results)

    def _internal_start_game(self):
        self.add_widget(self.game_widget)

    def _get_result(self):
        return int(sum(self.game_widget._scores) / len(self.game_widget._scores))

    def _format_result_to_display(self, result):
        return "%dms / bug" % result
    