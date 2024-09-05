import json
import os
from typing import Union
from os.path import abspath, dirname, exists
from os import makedirs


class LeaderboardEntry:

	def __init__(self, name: str, score: float):
		self._name = name
		self._score = score

	def get_name(self) -> str:
		return self._name

	def get_score(self) -> float:
		return self._score


class Leaderboard:

	def __init__(self, file_name: str, descending: bool = True):
		self.file_name = file_name
		self.descending = descending
		self.create_paths()
		self.scores: list[LeaderboardEntry] = []
		if exists(self.get_save_path()):
			with open(self.get_save_path(), 'r') as f:
				pairs = json.loads(f.read())
			if not isinstance(pairs, dict):
				return
			for name, score in pairs.items():
				self.add_score(LeaderboardEntry(name, score))
			print("Database Loaded for challenge " + file_name)
		print(self.get_save_path())

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
		return self.scores[:min(max_entries, len(self.scores))]

	def get_save_path(self) -> str:
		return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + "/HackersBenchmark/" + self.file_name + ".json"
		# return "Desktop/HackersBenchmark/" + self.file_name + ".json"

		# return abspath("leaderboards/" + self.file_name + ".json")

	def create_paths(self):
		path = self.get_save_path()
		os.makedirs(dirname(path), exist_ok=True)

	def save(self):
		self.create_paths()
		pairs = {p.get_name(): p.get_score() for p in self.scores}
		with open(self.get_save_path(), 'w') as save_file:
			save_file.write(json.dumps(pairs, indent=4))
