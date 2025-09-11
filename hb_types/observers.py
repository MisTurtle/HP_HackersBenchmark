from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

class Subject(ABC):

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass


class SimpleSubject(Subject):

    _observers: List[Observer] = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self):
        for obs in self._observers:
            obs.update(self)


class Observer(ABC):

    @abstractmethod
    def update(self, subject: Subject) -> None:
        pass

