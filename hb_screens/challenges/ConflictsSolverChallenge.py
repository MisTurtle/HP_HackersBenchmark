from hb_screens.challenge_screen import ChallengeScreen
from hb_types.game_widgets import BugHunterGameWidget, LatencyTimeWidget, SequenceMemoryWidget
from hb_types.widgets import TextWidget
from hb_utils.factories import ColorProvider, FontProvider, SpriteProvider
from hb_utils.leaderboard import Leaderboard
from hb_utils.maths import auto_width


class ConflictsSolverChallenge(ChallengeScreen):

    @staticmethod
    def get_leaderboard() -> Leaderboard:
        return Leaderboard("Conflicts Solver", False)

    def __init__(self, player_info):
        super().__init__("Conflicts Solver", "Évidemment, des conflits avec la base de code étaient inévitables. Il faut tous les régler un par un, c'est un vrai puzzle !\n\nGarde en mémoire la séquence qui s'affiche à l'écran, puis reproduit la.", False, player_info)
    
    def prepare_game(self):
        super().prepare_game()
        self.state_text = TextWidget("Suite de 1", font=FontProvider.get(("JACK.TTF", 42)), color=ColorProvider.get('fg'), align='center', rel_x=0.5, rel_y=0.4, rel_width=0.8, rel_height=0.4)
        self.game_widget = SequenceMemoryWidget(rel_x=0.53, rel_y=0.65, rel_height=0.5, rel_width=auto_width(0.5, (150, 150), self.get_rect().size), on_complete=self.display_results, on_step=self.update_text)

    def update_text(self):
        self.state_text.text = "Suite de %d" % len(self.game_widget.sequence)

    def _internal_start_game(self):
        self.add_widget(self.game_widget)
        self.add_widget(self.state_text)

    def _get_result(self):
        return len(self.game_widget.sequence) - 1

    def _format_result_to_display(self, result):
        return "Suite de %d" % result
    