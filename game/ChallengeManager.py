from game import Challenge
from game.types.AimChallenge import AimChallenge
from game.types.ReactionTimeChallenge import ReactionTimeChallenge
from game.types.SequenceMemoryChallenge import SequenceMemoryChallenge
from game.types.TimeMasterChallenge import TimeMasterChallenge
from game.types.TypingChallenge import TypingChallenge


class ChallengeManager:

	def __init__(self):
		self._challenges = []

	def get_challenge_count(self) -> int:
		return len(self._challenges)

	def get_challenges(self) -> list[Challenge]:
		return self._challenges

	def get_challenge(self, _id: int) -> Challenge:
		return self._challenges[_id] or None

	def add_challenge(self, c):
		self._challenges.append(c)

	def init_challenges(self):
		self.add_challenge(TypingChallenge())
		self.add_challenge(AimChallenge())
		self.add_challenge(TimeMasterChallenge())
		self.add_challenge(ReactionTimeChallenge())
		self.add_challenge(SequenceMemoryChallenge())

