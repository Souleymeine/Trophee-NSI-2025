#!/usr/bin/python

# Projet : pyscape
# Auteurs : Rabta Souleymeine

import multiprocessing
import sys
import os
from data_types import RGB, Coord
from escape_sequences import print_bgcolor_at
import input_processing
import input_properties
import terminal
from input_properties import MouseInfo, MouseButton
from terminal import Info, TerminalInfoManager, TerminalInfoProxy
from multiprocessing import Lock, Process, Queue
from threading import Thread
from event_listeners import listeners
if sys.platform != "win32":
    import signal

def clean_exit():
    terminal.reset(shared_terminal_state)
    terminal_info_manager.shutdown()
    input_process.kill()

    sys.exit(0)

if sys.platform != "win32":
    def sigterm_handler(signum, frame):
        clean_exit()

def event_reciever():
    # On écoute ensuite les évènements envoyé par "InputProcess"
    # les listes mouse_listeners, key_listeners, arrow_listeners et resize_listeners sont modifiée dynamiquement dans le processus principal
    # ailleur dans le programme par l'usage de décorateur
    while True:
        event_info = event_queue.get()
        match type(event_info):
            case input_properties.MouseInfo:
                for listener in listeners.mouse_listeners:
                    listener(event_info)
            case input_properties.KeyInfo:
                for listener in listeners.key_listeners:
                    listener(event_info)
            case input_properties.ArrowInfo:
                for listener in listeners.arrow_listeners:
                    listener(event_info)
            case os.terminal_size:
                for listener in listeners.resize_listeners:
                    listener(event_info)


@listeners.on_mouse
def paint(info: MouseInfo):
    brush_size = 5

    if info.click is not None and (info.click.button == MouseButton.LEFT or info.click.button == MouseButton.RIGHT):
        for x in range(-(brush_size * 2) + 1, 2*brush_size):
            for y in range(-brush_size + 1, brush_size):
                if info.coord.x + x >= 1 and info.coord.y + y >= 1:
                    color = RGB(0, int((info.coord.y/os.get_terminal_size().lines)*255), 0) if info.click.button == MouseButton.LEFT else RGB(0,0,0)
                    print_bgcolor_at(color, Coord(info.coord.x + x, info.coord.y + y))


if __name__ == "__main__":
    # NOTE : l'ordre des instructions suivantes est important !
    # Merci à ce post qui m'a permis de ne pas tomber dans la folie après plusieurs jours de recherches.
    # https://stackoverflow.com/questions/12492810/python-how-can-i-make-the-ansi-escape-codes-to-work-also-in-windows
    if sys.platform == "win32":
        os.system("") # Magie...
    else:
        signal.signal(signal.SIGTERM, sigterm_handler)

    terminal_info_manager = TerminalInfoManager()
    terminal_info_manager.register('Info', Info, TerminalInfoProxy)
    terminal_info_manager.start()
    

    shared_terminal_state = terminal_info_manager.Info() # type: ignore
    event_queue = Queue()
    lock = Lock()
    input_process = Process(target=input_processing.listen_to_input, args=(shared_terminal_state, event_queue), name="InputProcess")

    terminal.init(shared_terminal_state)

    input_process.start()

    event_listener_thread = Thread(target=event_reciever, daemon=True)
    event_listener_thread.start()
    
    input_process.join()

