from typing import Generic, TypeVar, Union, Callable

Kt = TypeVar('Kt')
Vt = TypeVar('Vt')


class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


class Provider(Generic[Kt, Vt]):

	def __init__(self):
		self.items: dict[Kt, Vt] = {}

	def get_all(self) -> dict[Kt, Vt]:
		return self.items

	def get(self, key: Kt, default: Union[Vt, None] = None) -> Union[Vt, None]:
		return self.items.get(key, default)

	def set(self, key: Kt, value: Vt):
		self.items[key] = value

	def rm(self, key: Kt):
		if key not in self.items:
			return
		del self.items[key]

	def clear(self):
		self.items.clear()


class LoadOnGetProvider(Provider[Kt, Vt]):

	def __init__(self, load_function: Callable[[Kt], Vt]):
		super().__init__()
		self.load_function = load_function

	def get(self, key: Kt, default: Union[Vt, None] = None) -> Union[Vt, None]:
		if key not in self.items and default is None:
			self.set(key, self.load_function(key))
		return super().get(key, default)
