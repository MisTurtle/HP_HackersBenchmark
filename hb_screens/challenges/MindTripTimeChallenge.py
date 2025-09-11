from hb_screens.challenge_screen import ChallengeScreen
from hb_types.game_widgets import LatencyTimeWidget
from hb_utils.factories import ColorProvider
from hb_utils.leaderboard import Leaderboard


class MindTripTimeChallenge(ChallengeScreen):
    
    @staticmethod
    def get_leaderboard() -> Leaderboard:
        return Leaderboard("Mind-Trip Time", False)

    def __init__(self, player_info):
        super().__init__("Mind-Trip Time", "Commençons par évaluer la latence de nos services.\n\nClique le plus vite possible sur l'écran dès qu'il devient vert. Répète ce procédé 3 fois pour confirmer la gravité de la situation.", True, player_info)
    
    def prepare_game(self):
        super().prepare_game()
        self.game_widget = LatencyTimeWidget(
            border_color=ColorProvider.get('fg'),
            rel_x=0.5, rel_y=0.5, rel_width=0.8, rel_height=0.65,
            on_complete=self.display_results
        )

    def _internal_start_game(self):
        self.add_widget(self.game_widget)

    def _get_result(self):
        return int(sum(self.game_widget.reaction_times) / len(self.game_widget.reaction_times))

    def _format_result_to_display(self, result):
        return "Latence: %dms" % result
    