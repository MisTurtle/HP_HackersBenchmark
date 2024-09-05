import math
import os.path
from typing import Callable, Any, Union, overload

import pygame


class SpriteAnimation:

	MODE_CLAMPED = 0
	MODE_CIRCULAR = 1

	def __init__(self,  spritesheet: pygame.Surface, frame_count: list[int], frame_time: list[float], frame_size: Union[tuple[int, int], None]):
		self.spritesheet = spritesheet
		self.frame_count = frame_count
		self.frame_time = frame_time
		self.frame_size = frame_size if frame_size is not None else (int(spritesheet.get_width() / frame_count[0]), int(spritesheet.get_height() / len(frame_count)))
		self.forced_frame_id = None

		self.animation_row = 0
		self.animation_time = 0  # seconds
		self.mode = self.MODE_CLAMPED

	def force_frame_id(self, frame_id: Union[int, None]) -> 'SpriteAnimation':
		self.forced_frame_id = frame_id
		return self

	def set_animation_progress(self, progress: float) -> 'SpriteAnimation':
		"""
		:param progress: Animation progress as a [0; 1] float
		:return: self
		"""
		self.forced_frame_id = round(self.get_frame_count() * progress)
		return self

	def set_mode(self, mode: int) -> 'SpriteAnimation':
		self.mode = mode
		return self

	def get_mode(self) -> int:
		return self.mode

	def tick(self, dt: float):
		self.animation_time += dt

	def get_frame_count(self) -> int:
		return self.frame_count[self.animation_row]

	def get_frame_time(self) -> float:
		return self.frame_time[self.animation_row]

	def get_frame_size(self) -> tuple[int, int]:
		return self.frame_size

	def get_spritesheet(self) -> pygame.Surface:
		return self.spritesheet

	def get_animation_row(self) -> int:
		return self.animation_row

	def get_animation_start(self) -> float:
		return self.animation_time

	def set_animation_row(self, row: int) -> 'SpriteAnimation':
		if row < 0 or row >= len(self.frame_count):
			raise ValueError("Provided animation row value is bigger than the spritesheet height")
		if self.frame_count[row] == 0:
			raise ValueError("Provided animation row value is not yet implemented (Empty row)")
		self.animation_row = row
		self.animation_time = 0
		return self

	def get_frame_coords(self) -> tuple[int, int]:
		if self.get_mode() == self.MODE_CLAMPED:
			return int(self.animation_time // self.frame_time[self.animation_row]) % self.frame_count[self.animation_row] if self.forced_frame_id is None else self.forced_frame_id, self.animation_row
		if self.get_mode() == self.MODE_CIRCULAR:
			progress = self.animation_time / (self.frame_time[self.animation_row] * self.get_frame_count())
			return int(self.get_frame_count() * (1 + math.sin(progress * math.pi / 2)) / 2), self.animation_row

	def extract(self) -> pygame.Surface:
		coords = self.get_frame_coords()
		offset = coords[0] * self.frame_size[0], coords[1] * self.frame_size[1]
		frame_end = offset[0] + self.frame_size[0], offset[1] + self.frame_size[1]
		clamp_factor = max(0, frame_end[0] - self.spritesheet.get_width()), max(0, frame_end[1] - self.spritesheet.get_height())
		# print(offset, frame_end, clamp_factor)
		return self.spritesheet.subsurface(offset, (self.frame_size[0] - clamp_factor[0], self.frame_size[1] - clamp_factor[1])).copy()


class Animation:

	STATE_PAUSED = 0
	STATE_RUNNING = 1

	@staticmethod
	def PAUSE_ON_END(animation: 'Animation'):
		animation.pause()

	@staticmethod
	def REWIND_ON_END(animation: 'Animation'):
		animation.reverse()

	@staticmethod
	def RESET_ON_END(animation: 'Animation'):
		animation.reset()

	def __init__(self, duration: float):
		"""
		:param duration: Animation duration (in seconds)
		"""
		assert duration > 0
		self._state = self.STATE_PAUSED
		self._duration = duration
		self._progress = 0
		self._progress_speed = 1  # Progress time per second (x seconds of the animation passes every realtime second)
		self._on_end_behavior: Callable[[Animation], Any] = Animation.PAUSE_ON_END
		self._on_complete_calls: list[Callable[[], Any]] = []

	def get_duration(self) -> float:
		return self._duration

	def is_running(self):
		return self._state == self.STATE_RUNNING

	def start(self) -> 'Animation':
		self._state = self.STATE_RUNNING
		return self

	def pause(self) -> 'Animation':
		self._state = self.STATE_PAUSED
		return self

	def reverse(self) -> 'Animation':
		self._progress_speed *= -1
		return self

	def reset(self) -> 'Animation':
		self._state = self.STATE_PAUSED
		self._progress = 0
		self._progress_speed = 1
		return self

	def set_speed(self, speed: float) -> 'Animation':
		"""
		Changes the animation's speed (Unit is in steps per second)
		:return:
		"""
		self._progress_speed = speed
		return self

	def speed_up(self, by: float) -> 'Animation':
		self._progress_speed *= by
		return self

	def slow_down(self, by: float) -> 'Animation':
		return self.speed_up(1 / by)

	def get_speed(self) -> float:
		return self._progress_speed

	def get_progress(self) -> float:
		return self._progress

	def get_progress_percent(self) -> float:
		return self._progress / self._duration

	def set_end_behavior(self, callback: Callable[['Animation'], Any]) -> 'Animation':
		self._on_end_behavior = callback
		return self

	def then(self, callback: Callable[[], Any]):
		self._on_complete_calls.append(callback)

	def set_progress_percent(self, progress: float):
		self._progress = self._duration * progress

	def tick(self, dt: float):
		if not self.is_running() or self._progress_speed == 0:
			return
		new_progress = self._progress + self._progress_speed * dt
		self._progress = min(self._duration, new_progress) if self._progress_speed > 0 else max(0., new_progress)
		if (self._progress_speed > 0 and self._progress >= self._duration) or (self._progress_speed < 0 and self._progress == 0):
			for callback in self._on_complete_calls:
				callback()
			self._on_complete_calls.clear()
			self._on_end_behavior(self)


class PulseSettings:

	def __init__(self, period: float, amplitude: float, base: tuple[float, float]):
		self._period = period
		self._amp = amplitude
		self._base = base

	def get_period(self) -> float:
		return self._period

	def set_period(self, period: float) -> 'PulseSettings':
		self._period = period
		return self

	def reduce_period(self, by_s: float) -> 'PulseSettings':
		self._period -= by_s
		return self

	def increase_period(self, by_s: float) -> 'PulseSettings':
		return self.reduce_period(-by_s)

	def divide_period(self, by: float) -> 'PulseSettings':
		self._period /= by
		return self

	def multiply_period(self, by: float) -> 'PulseSettings':
		self._period *= by
		return self

	def get_amp(self) -> float:
		return self._amp

	def reduce_amp(self, by_pc: float) -> 'PulseSettings':
		self._amp -= by_pc
		return self

	def increase_amp(self, by_pc: float) -> 'PulseSettings':
		return self.reduce_amp(-by_pc)

	def divide_amp(self, by: float) -> 'PulseSettings':
		self._amp /= by
		return self

	def multiply_amp(self, by: float) -> 'PulseSettings':
		self._amp *= by
		return self

	def set_amp(self, amp: float) -> 'PulseSettings':
		self._amp = amp
		return self

	def get_base(self) -> tuple[float, float]:
		return self._base

	def set_base(self, base: tuple[float, float]) -> 'PulseSettings':
		self._base = base
		return self

	def compute(self, duration: float):
		f = self.get_amp() * math.sin(math.pi * duration / self.get_period()) / 2
		return self._base[0] + f, self._base[1] + f


class FontSettings:

	def __init__(self, font_path: str, font_size: int, color: pygame.Color):
		self._font_path = font_path
		self._font_size = font_size
		if os.path.exists(font_path):
			self._font = pygame.font.Font(font_path, font_size)
		else:
			self._font = pygame.font.SysFont(font_path, font_size)
		self._color = color
		self._dirty = False

	def get_font_path(self) -> str:
		return self._font_path

	def get_font_size(self) -> int:
		return self._font_size

	def get_font(self) -> pygame.font.Font:
		return self._font

	def set_font(self, font_path: str, font_size: int) -> 'FontSettings':
		self._font = pygame.font.Font(font_path, font_size)
		self._dirty = True
		return self

	def get_color(self) -> pygame.Color:
		return self._color

	def set_color(self, color: pygame.Color) -> 'FontSettings':
		self._color = color
		return self

	def is_dirty(self) -> bool:
		return self._dirty

	def clear_dirty(self):
		self._dirty = False

	def render_line(self, line: str):
		return self._font.render(line, True, self._color)

	def copy(self) -> 'FontSettings':
		return FontSettings(self._font_path, self._font_size, self._color)


class TimerTrigger:

	DROPS_BELOW = 0
	REACHES = 1
	IS_BETWEEN = 2

	def __init__(self, trigger_type: int, threshold: Union[float, tuple[float, float]], handler: Callable[[], Any], rm_on_trigger: bool = True):
		if trigger_type != TimerTrigger.IS_BETWEEN and isinstance(threshold, tuple):
			raise ValueError("Timer trigger window can only be a range when trigger type is TimerTrigger.IS_BETWEEN (" + str(
				TimerTrigger.IS_BETWEEN) + ")")
		self.trigger_type = trigger_type
		self.threshold = threshold
		self.handler = handler
		self.rm_on_trigger = rm_on_trigger

	def is_applicable(self, _from: Union[float, None], _to: float):
		match self.trigger_type:
			case self.DROPS_BELOW:
				return _from >= self.threshold >= _to if _from is not None else self.threshold >= _to
			case self.REACHES:
				return _from <= self.threshold <= _to if _from is not None else self.threshold <= _to
			case self.IS_BETWEEN:
				self.threshold: tuple[float, float]
				return self.threshold[0] >= _to >= self.threshold[1]



