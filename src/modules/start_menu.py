from type_def.data_types import RGB, Anchor, Coord
from core.escape_sequences import ANSI_Styles, print_at
from type_def.input_properties import MouseButton, MouseInfo
from tui.base import ColorsOnMouse, Positioning
from tui.button import Button
from threading import Thread
import time

def click_button(info: MouseInfo):
    if info.click is not None and info.click.button == MouseButton.LEFT:
        Thread(target=show_text).start()

def show_text():
    print_at("Cliqué !", Coord(3, 2))
    time.sleep(2)
    print_at("\x1b[0K", Coord(3, 2))

def start_menu():
    button = Button(
        Positioning(Coord(15, 5), Anchor.TOP_LEFT, 14, 5), "Bouton", ANSI_Styles.ITALIC, 
        ColorsOnMouse(hover_bg_col=RGB(50, 50, 50), click_bg_col=RGB(20,20,20)),
        rounded=True
    )

    button.on_click = click_button
