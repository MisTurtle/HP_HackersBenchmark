import json
import os
from typing import Union


class LeaderboardEntry:

    def __init__(self, name: str, score: float):
        self._name = name
        self._score = score

    def get_name(self) -> str:
        return self._name

    def get_score(self) -> float:
        return self._score


class Leaderboard:

    ROOT_PATH = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + "/HackersBenchmark/"

    def __init__(self, file_name: str, descending: bool = True):
        self.file_name = file_name
        self.descending = descending
        self.scores: list[LeaderboardEntry] = []
        
        os.makedirs(os.path.dirname(self.get_save_path()), exist_ok=True)
        
        if os.path.exists(self.get_save_path()):
            with open(self.get_save_path(), 'r') as f:
                pairs = json.loads(f.read())
            if not isinstance(pairs, dict):
                return
            for name, score in pairs.items():
                self.add_score(LeaderboardEntry(name, score))
            print("Database Loaded for challenge " + file_name)

    def get_prev_entry(self, name: str) -> Union[LeaderboardEntry, None]:
        for prev in self.scores:
            if prev.get_name().lower() == name.lower():
                return prev
        return None

    def improves(self, entry: LeaderboardEntry) -> bool:
        prev = self.get_prev_entry(entry.get_name())
        return prev is None or (self.descending and prev.get_score() < entry.get_score()  or  not self.descending and prev.get_score() > entry.get_score())

    def add_score(self, entry: LeaderboardEntry):
        # Find out if this is any improvement from the user
        if not self.improves(entry):
            return  # Skip if it's not
        prev = self.get_prev_entry(entry.get_name())
        if prev is not None:
            self.scores.remove(prev)
        self.scores.append(entry)
        self.scores.sort(key=lambda _e: _e.get_score(), reverse=self.descending)
        self.save()

    def get_rank(self, player: str):
        player = player.lower()
        for rank, entry in enumerate(self.scores):
            if entry.get_name().lower() == player:
                return rank + 1
        return -1

    def get_top(self, max_entries: int = 10) -> list[LeaderboardEntry]:
        return self.scores[:max_entries]

    def get_save_path(self) -> str:
        return Leaderboard.ROOT_PATH + self.file_name + ".json"

    def save(self):
        pairs = {p.get_name(): p.get_score() for p in self.scores}
        with open(self.get_save_path(), 'w') as save_file:
            save_file.write(json.dumps(pairs, indent=4))


def get_best_average_placement(leaderboards):
    # Collect all unique players
    players = set()
    for lb in leaderboards:
        for entry in lb.scores:
            players.add(entry.get_name())

    # Calculate average rank for each player
    player_avg_ranks = {}
    for player in players:
        total_rank = 0
        num_leaderboards = 0
        for lb in leaderboards:
            rank = lb.get_rank(player)
            if rank != -1:  # Player exists in this leaderboard
                total_rank += rank
                num_leaderboards += 1
        if num_leaderboards > 0:
            avg_rank = total_rank / num_leaderboards
            player_avg_ranks[player] = avg_rank

    # Sort players by average rank (ascending, since lower is better)
    sorted_players = sorted(player_avg_ranks.items(), key=lambda x: x[1])

    return sorted_players