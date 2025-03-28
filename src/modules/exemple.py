import os
from tests.tests import print_sized_dialog
from tui.box import Box
from tui.surface import Surface
from tui.text_area import TextArea
from type_def.data_types import RGB, Anchor, Coord
from core.escape_sequences import ANSI_Styles, goto, print_at, print_bgcolor_at
from type_def.input_properties import MouseButton, MouseInfo
from tui.base import ColorsOnMouse, Positioning
from tui.button import Button
from threading import Thread
import time

def click_button(info: MouseInfo):
    if info.click is not None and info.click.button == MouseButton.LEFT:
        Thread(target=show_text).start()

def print_dialog(info: MouseInfo):
    if info.click is not None and info.click.button == MouseButton.LEFT and info.click.released:
        goto(Coord(1, os.get_terminal_size().lines - 10))
        Thread(target=print_sized_dialog, args=("Un joli text, ponctué et \"lu\" correctement. On pourrait imaginer un jeu vidéo avec un système de dialogue.", 25)).start()

def show_text():
    print_at("Cliqué !", Coord(4, 7))
    time.sleep(2)
    print_at("         ", Coord(4, 7))

def paint(info: MouseInfo):
    brush_size: int = 3
    assert info.click is not None
    if (info.click.button == MouseButton.LEFT or info.click.button == MouseButton.RIGHT):
        for x in range(-(brush_size * 2) + 1, 2*brush_size):
            for y in range(-brush_size + 1, brush_size):
                if info.coord.x + x >= 1 and info.coord.y + y >= 1:
                    if info.click.button == MouseButton.LEFT:
                        color = RGB(0, int((info.coord.y/os.get_terminal_size().lines)*255), 0)
                        print_bgcolor_at(color, Coord(info.coord.x + x, info.coord.y + y))
                    else:
                        print_at(' ', Coord(info.coord.x + x, info.coord.y + y))

def exemple():
    surface = Surface(Positioning(Coord(36, 4), Anchor.TOP_LEFT, 78, 24))
    button = Button(
        Positioning(Coord(1, 1), Anchor.TOP_LEFT, 15, 5), "Un bouton", ANSI_Styles.ITALIC, 
        ColorsOnMouse(hover_bg_col=RGB(50, 50, 50), click_bg_col=RGB(20,20,20)),
        rounded=False
    )
    
    dialog_button = Button(
        Positioning(Coord(1, 9), Anchor.TOP_LEFT, 14, 5), "Un autre", ANSI_Styles.DEFAULT, 
        ColorsOnMouse(hover_bg_col=RGB(75, 50, 50), click_bg_col=RGB(20,20,50)),
        rounded=True
    )

    Box(Positioning(Coord(30, 1), Anchor.TOP_LEFT, 90, 30))
    
    TextArea(Positioning(Coord(123, 3), Anchor.TOP_LEFT, 50, 21), "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris vestibulum, mi in pellentesque consequat, felis tortor tincidunt odio, ac maximus neque ex at tortor. Proin et cursus tortor. Vestibulum at erat nec odio placerat commodo. Suspendisse id pretium diam. Proin consectetur justo nulla, sit amet dignissim augue rutrum ut. Etiam pharetra nisl orci, vel mollis risus euismod in. Aliquam posuere nunc arcu, at faucibus elit tristique et. Ut eu nisl vestibulum, sagittis tortor nec, malesuada ante. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.\n\nhttps://www.google.com/search?q=genere+moi+un+long+lien+pour+mon+test+merci&client=firefox-b-d&sca_esv=218665eea446f0ac&ei=gdXlZ833EOickdUP-LigyAY&ved=0+pour+mon+test+merci",
        ANSI_Styles.ITALIC, ColorsOnMouse(default_fg_col=RGB(125, 125, 255), hover_fg_col=RGB(125, 125, 125)))

    surface.on_click = paint
    button.on_click = click_button
    dialog_button.on_click = print_dialog
