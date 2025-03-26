# from multiprocessing.managers import BaseManager, BaseProxy
from os import terminal_size
from typing import Callable, Any

from type_def.data_types import EnsureSingle
from type_def.input_properties import ArrowInfo, KeyInfo, MouseInfo

class EventListenerSubscriber(metaclass=EnsureSingle):
    def __init__(self) -> None:
        self.mouse_listeners:  list[Callable[[MouseInfo],     Any]] = []
        self.key_listeners:    list[Callable[[KeyInfo],       Any]] = []
        self.arrow_listeners:  list[Callable[[ArrowInfo],     Any]] = []
        self.resize_listeners: list[Callable[[terminal_size], Any]] = []

    def on_mouse(self, callback: Callable[[MouseInfo], Any]):
        self.mouse_listeners.append(callback)

    def on_key(self, callback: Callable[[KeyInfo], Any]):
        self.key_listeners.append(callback)

    def on_arrow(self, callback: Callable[[ArrowInfo], Any]):
        self.arrow_listeners.append(callback)

    def on_resize(self, callback: Callable[[terminal_size], Any]):
        self.resize_listeners.append(callback)

listeners = EventListenerSubscriber()
