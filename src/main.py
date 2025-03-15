#!/usr/bin/python

# Projet : pyscape
# Auteurs : Rabta Souleymeine

import signal
import sys
import asyncio
import input_processing
import terminal

async def main():
    terminal.init()

    input_processing.input_process.start()
    input_processing.input_process.join()

def exit_gracefully(signum, frame):
    input_processing.input_process.kill()
    terminal.reset()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_gracefully)  # Capture CTRL+C
    asyncio.run(main())

# Enfaite ici ça dépends si on a des problèmes avec signal, parce que apparemment sur windows ça marche pas très bien.
# except KeyboardInterrupt:
# exit_gracefully()
