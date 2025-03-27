from dataclasses import dataclass
from os import terminal_size
from typing import Callable, Any

from type_def.data_types import EnsureSingle
from type_def.input_properties import ArrowInfo, KeyInfo, MouseInfo

@dataclass
class MouseCallbacks:
    on_hover: Callable[[MouseInfo], Any]
    on_click: Callable[[MouseInfo], Any]
    on_exit: Callable[[MouseInfo], Any]

class EventListenerSubscriber(metaclass=EnsureSingle):
    def __init__(self) -> None:
        self.mouse_listeners:  dict[object, MouseCallbacks] = {}
        self.key_listeners:    dict[object, Callable[[KeyInfo],           Any]] = {}
        self.arrow_listeners:  dict[object, Callable[[ArrowInfo],         Any]] = {}
        self.resize_listeners: dict[object, Callable[[terminal_size],     Any]] = {}

    def register_mouse_callbacks(self, obj: object, callbacks: MouseCallbacks):
        self.mouse_listeners[obj] = callbacks
    def register_key(self, obj: object, callback: Callable[[KeyInfo], Any]):
        self.key_listeners[obj] = callback
    def register_arrow(self, obj: object, callback: Callable[[ArrowInfo], Any]):
        self.arrow_listeners[obj] = callback
    def register_resize(self, obj: object, callback: Callable[[terminal_size], Any]):
        self.resize_listeners[obj] = callback

listeners = EventListenerSubscriber()

