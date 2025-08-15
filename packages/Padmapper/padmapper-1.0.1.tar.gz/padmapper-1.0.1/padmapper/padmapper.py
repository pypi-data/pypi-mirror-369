#!/usr/bin/python3

import sys
import json
from threading import Thread

from .Keyboard import Keyboard
from .Mouse import Mouse
from .Padmapper import Padmapper
from .Params import Params

from time import sleep

def main():
    if len(sys.argv) != 2:
        print("Usage: %s <config.json>" % sys.argv[0])
        sys.exit(1)

    config_file = open(sys.argv[1], "r")
    config = json.load(config_file)
    config_file.close()

    params = Params(config)
    keyboard = Keyboard()
    mouse = Mouse(params)

    padmapper = Padmapper(keyboard, mouse, config, params)

    def padmapper_task():
        padmapper.handle_events()

    padmapper_thread = Thread(target=padmapper_task, daemon=True)
    padmapper_thread.start()

    try:
        while True:
            sleep(10)
    except (KeyboardInterrupt, SystemExit):
        print("Terminating padmapper")
        padmapper.quit()
        padmapper_thread.join()
        del padmapper
        del keyboard
        del mouse

if __name__ == "__main__":
    main()
