#!/usr/bin/python

# Projet : pyscape
# Auteurs : Rabta Souleymeine

import sys
import os
import core.input_processing as input_processing
import type_def.input_properties as input_properties
import core.terminal as terminal
from core.terminal import Info, TerminalInfoManager, TerminalInfoProxy
from multiprocessing import Process, Queue
from core.event_listeners import listeners
from modules.start_menu import start_menu
from core.event_managers import manage_mouse_event, manage_key_event, manage_arrow_event, manage_resize_event


if sys.platform != "win32":
    import signal

def clean_exit():
    terminal.reset(shared_terminal_state)
    input_process.kill()
    terminal_info_manager.shutdown()

    sys.exit(0)

if sys.platform == "win32":
    @listeners.on_resize
    def correct_hidden_windows_cursor(info):
        hide_cursor()
else:
    def sigterm_handler(signum, frame):
        clean_exit()

def main():
    # On écoute ensuite les évènements envoyé par "InputProcess"
    while True:
        event_info = event_queue.get()
        if event_info == "END":
            clean_exit()
            break
        match type(event_info):
            case input_properties.MouseInfo: manage_mouse_event(event_info, listeners)
            case input_properties.KeyInfo:   manage_key_event(event_info, listeners)
            case input_properties.ArrowInfo: manage_arrow_event(event_info, listeners)
            case os.terminal_size:           manage_resize_event(event_info, listeners)

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
    input_process = Process(target=input_processing.listen_to_input, args=(shared_terminal_state, event_queue), name="InputProcess")

    terminal.init(shared_terminal_state)

    input_process.start()


    start_menu()

    main()
