#!/usr/bin/python

# Projet : pyscape
# Auteurs : Rabta Souleymeine

import sys
import os
import input_processing
import input_properties
import terminal
from terminal import Info, TerminalInfoManager, TerminalInfoProxy
from multiprocessing import Process, Queue
from threading import Thread
from event_listeners import listeners
if sys.platform != "win32":
    import signal

def clean_exit():
    input_process.kill()
    terminal.reset(shared_terminal_state)
    terminal_info_manager.shutdown()

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

    event_listener_thread = Thread(target=event_reciever, daemon=True)
    event_listener_thread.start()
    
@listeners.on_mouse
def a(info):
    print(f"Exemple : {info}", end="\r\n")
