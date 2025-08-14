#!/usr/bin/env python3
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict

#=================================================================#
# Notificadores e observadores
#=================================================================#
# Sujeito notificador
class AbstractNotifyProvider(ABC):
    def __init__(self):
        self.observer_list: List[AbstractObserver] = []
        self.num_observers: int = 0

    def add_observer(self, observer: AbstractObserver):
        self.observer_list.append(observer)
        self.num_observers += 1
        print(f'Obsevador adicionado: {self.num_observers}')

    def remove_observer(self, observer: AbstractObserver):
        if len(self.observer_list) < 1:
            return
        self.observer_list.remove(observer)
        self.num_observers -= 1

    def clear(self):
        self.observer_list.clear()
        self.num_observers = 0

    def send_notify(self):
        for obs in self.observer_list:
            obs.receiver_notify(self)

# Sujeito Observador
class AbstractObserver(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def receiver_notify(self, notify_provide: AbstractNotifyProvider = None):
        """Receber atualizações."""
        pass


class ControllerNotifyProvider(AbstractNotifyProvider):
    def __init__(self):
        super().__init__()
        self.observer_list: List[ObserverController] = []

    def send_notify_theme(self):
        for obs in self.observer_list:
            obs.receiver_notify_theme(self)

    def send_notify_files(self):
        for obs in self.observer_list:
            obs.receiver_notify_files(self)
        print(f'{__class__.__name__} Alteraçõs de arquivos notificada!')

class ObserverController(AbstractObserver):
    def __init__(self):
        super().__init__()

    def receiver_notify_files(self, notify: ControllerNotifyProvider):
        pass

    def receiver_notify_theme(self, notify: ControllerNotifyProvider):
        pass
