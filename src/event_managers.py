import os
from input_properties import ArrowInfo, KeyInfo, MouseInfo
from event_listeners import EventListenerSubscriber
from tui.base import ClickableElement


def manage_mouse_event(event_info: MouseInfo, listeners: EventListenerSubscriber):
    # Gestion basique de la souris
    for clickable_element, mouse_callbacks in list(listeners.mouse_listeners.items()):
        assert type(clickable_element) == ClickableElement
        top_left_coord = clickable_element.top_left_coord
        horizontal_align: bool = top_left_coord.x <= event_info.coord.x <= top_left_coord.x + clickable_element.positioning.width
        vertical_align: bool = top_left_coord.y <= event_info.coord.y <= top_left_coord.y + clickable_element.positioning.height
        if horizontal_align and vertical_align:
            if event_info.click is not None:
                mouse_callbacks.on_click(event_info)
            else:
                mouse_callbacks.on_hover(event_info)
        elif clickable_element.is_mouse_over == True:
            clickable_element.is_mouse_over = False
            mouse_callbacks.on_exit(event_info)

def manage_key_event(event_info: KeyInfo, listeners: EventListenerSubscriber):
    for tui_element, key_callback in listeners.key_listeners.items():
        key_callback(event_info)

def manage_arrow_event(event_info: ArrowInfo, listeners: EventListenerSubscriber):
    for tui_element, arrow_callback in listeners.arrow_listeners.items():
        arrow_callback(event_info)

def manage_resize_event(event_info: os.terminal_size, listeners: EventListenerSubscriber):
    for tui_element, resize_callback in listeners.resize_listeners.items():
        resize_callback(event_info)
