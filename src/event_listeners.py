# from multiprocessing.managers import BaseManager, BaseProxy
from os import terminal_size
from typing import Callable, Any, Self

from data_types import EnsureSingle
from input_properties import ArrowInfo, KeyInfo, MouseInfo

class EventListenerSubscriber(metaclass=EnsureSingle):
    def __init__(self) -> None:
        self.object_mouse_listeners:  list[Callable[[Self | MouseInfo],     Any]] = []
        self.object_key_listeners:    list[Callable[[Self | KeyInfo],       Any]] = []
        self.object_arrow_listeners:  list[Callable[[Self | ArrowInfo],     Any]] = []
        self.object_resize_listeners: list[Callable[[Self | terminal_size], Any]] = []

        self.mouse_listeners:  list[Callable[[MouseInfo],     Any]] = []
        self.key_listeners:    list[Callable[[KeyInfo],       Any]] = []
        self.arrow_listeners:  list[Callable[[ArrowInfo],     Any]] = []
        self.resize_listeners: list[Callable[[terminal_size], Any]] = []

    # TODO : remplacer object par tui_element
    def on_mouse(self, callback: Callable[[MouseInfo], Any]):
        self.mouse_listeners.append(callback)

    def on_key(self, callback: Callable[[KeyInfo], Any]):
        self.key_listeners.append(callback)

    def on_arrow(self, callback: Callable[[ArrowInfo], Any]):
        self.arrow_listeners.append(callback)

    def on_resize(self, callback: Callable[[terminal_size], Any]):
        self.resize_listeners.append(callback)

listeners = EventListenerSubscriber()
