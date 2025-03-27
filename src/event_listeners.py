# from multiprocessing.managers import BaseManager, BaseProxy
from dataclasses import dataclass
from os import terminal_size
from typing import Callable, Any

from TUI_elements.TUI_element import TUIElement
from data_types import EnsureSingle
from input_properties import ArrowInfo, KeyInfo, MouseInfo

@dataclass
class TUIElementMouseCallbacks:
    on_hover: Callable[[MouseInfo], Any]
    on_exit: Callable[[MouseInfo], Any]
    on_click: Callable[[MouseInfo], Any]

class EventListenerSubscriber(metaclass=EnsureSingle):
    def __init__(self) -> None:
        self.mouse_listeners:  dict[TUIElement, TUIElementMouseCallbacks] = {}
        self.key_listeners:    dict[TUIElement, Callable[[KeyInfo],           Any]] = {}
        self.arrow_listeners:  dict[TUIElement, Callable[[ArrowInfo],         Any]] = {}
        self.resize_listeners: dict[TUIElement, Callable[[terminal_size],     Any]] = {}

    def register_mouse_callbacks(self, obj: TUIElement, callbacks: TUIElementMouseCallbacks):
        self.mouse_listeners[obj] = callbacks
    def register_key(self, obj: TUIElement, callback: Callable[[KeyInfo], Any]):
        self.key_listeners[obj] = callback
    def register_arrow(self, obj: TUIElement, callback: Callable[[ArrowInfo], Any]):
        self.arrow_listeners[obj] = callback
    def register_resize(self, obj: TUIElement, callback: Callable[[terminal_size], Any]):
        self.resize_listeners[obj] = callback

listeners = EventListenerSubscriber()
