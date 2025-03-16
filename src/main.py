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

def clean_exit():
    input_processing.input_process.kill()
    terminal.reset()
    sys.exit(0)


if sys.platform != "win32":
    def sigint_handler(signum, frame):
        clean_exit()

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            clean_exit()
    else:
        signal.signal(signal.SIGINT, sigint_handler)  # Capture CTRL+C
        asyncio.run(main())

