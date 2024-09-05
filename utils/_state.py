from utils import Singleton


class _AppState(metaclass=Singleton):

	_TARGET_FRAME_RATE = 60
	_FPS_HISTORY_SIZE = 60

	_running = True
	_fps_history = []

	def __init__(self):
		self._fps_history = [self._TARGET_FRAME_RATE] * self._FPS_HISTORY_SIZE

	def is_running(self) -> bool:
		return self._running

	def stop(self):
		self._running = False

	def register_frame_time(self, fps: float):
		self._fps_history = [fps] + self._fps_history[:-1]

	def get_target_frame_rate(self) -> float:
		return self._TARGET_FRAME_RATE

	def get_frame_rate(self):
		return sum(self._fps_history) / self._FPS_HISTORY_SIZE


AppState = _AppState()
