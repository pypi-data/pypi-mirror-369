#!/usr/bin/python3

import pygame

def configure():
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    print("Pad %d button %d" % (event.joy, event.button))
                elif event.type == pygame.JOYAXISMOTION:
                    if event.axis > 1:
                        continue
                    print("Pad %d joystick axis motion: %d %d" % (event.joy, event.axis, event.value))
    except KeyboardInterrupt:
        pass

def main():
    pygame.init()
    joysticks = []
    for i in range(0, pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        print(joystick.get_name())
        joysticks.append(joystick)
    configure()

if __name__ == "__main__":
    main()
