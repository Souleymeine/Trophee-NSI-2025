#!/usr/bin/python

# Projet : pyscape
# Auteurs : Rabta Souleymeine

import sys
import os
import asyncio
import input_processing
import terminal
from terminal import Info, TerminalInfoManager, TerminalInfoProxy
from multiprocessing import Process

async def main():
    terminal.init(shared_terminal_state)
    
    input_process.start()
    input_process.join()

def clean_exit():
    input_process.kill()

    terminal.reset(shared_terminal_state)
    terminal_info_manager.shutdown()

    sys.exit(0)

if sys.platform != "win32":
    def sigint_handler(signum, frame):
        clean_exit()

if __name__ == "__main__":
    # NOTE : l'ordre des instructions suivantes est important !
    # Merci à ce post qui m'a permis de ne pas tomber dans la folie après plusieurs jours de recherches.
    # https://stackoverflow.com/questions/12492810/python-how-can-i-make-the-ansi-escape-codes-to-work-also-in-windows
    if sys.platform == "win32":
        os.system("") # Magie...

    terminal_info_manager = TerminalInfoManager()
    terminal_info_manager.register('Info', Info, TerminalInfoProxy)
    terminal_info_manager.start()
    shared_terminal_state = terminal_info_manager.Info() # type: ignore

    input_process = Process(target=input_processing.listen_to_input, args=(shared_terminal_state,), name="InputProcess", daemon=True)

    asyncio.run(main())

