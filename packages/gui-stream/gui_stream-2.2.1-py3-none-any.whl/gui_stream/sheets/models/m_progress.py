#!/usr/bin/env python3
#
from abc import ABC, abstractmethod

class ABCProgressBar(ABC):
    """
        Barra de progresso Abstrata
    """
    def __init__(self):
        super().__init__()
        self._current_progress = 0
        
    @property
    def current_progress(self) -> float:
        return self._current_progress
    
    @current_progress.setter
    def current_progress(self, new:float):
        if isinstance(new, float):
            self._current_progress = new
            return
        try:
            _prog = float(new)
        except Exception as e:
            print(e)
            self._current_progress = 0
        else:
            self._current_progress = _prog
    
    @abstractmethod
    def set_percent(self, percent_str: str):
        """Seta o progresso como uma string de porcentagem, ex: '42%'"""
        pass

    @abstractmethod
    def set_status_text(self, text: str):
        """Seta um texto indicando a situação atual"""
        pass

    def start(self):
        """Inicia a barra de progresso (pode ser vazio dependendo da implementação)"""
        pass

    def stop(self):
        """Para a barra de progresso (pode ser vazio dependendo da implementação)"""
        pass



