import pygame
from .Params import CombinedActionsBehavior

class Padmapper:
    keyboard = None
    mouse = None
    config = None
    params = None
    joysticks = []

    def __init__(self, keyboard, mouse, config, params):
        self.keyboard = keyboard
        self.mouse = mouse
        self.config = config
        self.params = params
        pygame.init()
        for i in range(0, pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            print(joystick.get_name())
            self.joysticks.append(joystick)

    def special_actions(self, actions, end=False):
        if actions['mouse'] != None:
            self.mouse.actions(actions['mouse'], end)

    def start_actions(self, actions):
        print("press {}".format(actions))
        for action in actions:
            if type(action) is dict:
                self.special_actions(action)
            else:
                self.keyboard.press(action)

    def stop_actions(self, actions):
        print("release {}".format(actions))
        for action in actions:
            if type(action) is dict:
                self.special_actions(action, end=True)
            else:
                self.keyboard.release(action)

    def is_joystick_axis_ignored(self, joy, axis):
        joyid = str(joy)
        if self.config[joyid]['joystick'].get('ignore') is not None \
                and str(axis) in self.config[joyid]['joystick']['ignore']:
            return True
        return False

    def get_joystick_state(self, joy):
        numaxes = self.joysticks[joy].get_numaxes()
        state = []
        for axis in range(0, numaxes):
            if self.is_joystick_axis_ignored(joy, axis):
                continue
            state.append(int(round(self.joysticks[joy].get_axis(axis))))
        return state

    def format_joystick_state(self, state):
        state_str = ""
        for axis in state:
            state_str = state_str + str(axis) + ':'
        return state_str[:-1]

    def handle_button_event(self, event):
        joyid = str(event.joy)
        button = str(event.button)
        actions = self.config[joyid]['buttons'][button]
        if event.type == pygame.JOYBUTTONDOWN:
            print("JOYBUTTONDOWN %d: %d => " % (event.joy, event.button), end='')
            self.start_actions(actions)
        elif event.type == pygame.JOYBUTTONUP:
            print("JOYBUTTONUP %d: %d => " % (event.joy, event.button), end='')
            self.stop_actions(actions)

    def update_joystick_combined_actions(self, event):
        ret = False
        joyid = str(event.joy)
        if self.config[joyid]['joystick'].get('combined') is None:
            return ret
        joy_state = self.format_joystick_state(self.get_joystick_state(event.joy))
        for combo in self.config[joyid]['joystick']['combined']:
            if combo == joy_state:
                self.start_actions(self.config[joyid]['joystick']['combined'][combo])
                ret = True
            else:
                self.stop_actions(self.config[joyid]['joystick']['combined'][combo])
        return ret

    def handle_joystick_event(self, event):
        if self.is_joystick_axis_ignored(event.joy, event.axis):
            return
        joyid = str(event.joy)
        axis = str(event.axis)
        direction = str(int(round(event.value)))
        print("JOYAXISMOTION %d: %d %d => " % (event.joy, event.axis, event.value), end='')
        if self.params.joystick_combined_actions_behavior <= CombinedActionsBehavior.BEFORE:
            ret = self.update_joystick_combined_actions(event)
            if ret and self.params.joystick_combined_actions_behavior == CombinedActionsBehavior.ONLY:
                return
        if direction != '0':
            actions = self.config[joyid]['joystick'][axis][direction]
            self.start_actions(actions)
        else:
            actions = []
            for direction in self.config[joyid]['joystick'][axis]:
                actions = actions + self.config[joyid]['joystick'][axis][direction]
            self.stop_actions(actions)
        if self.params.joystick_combined_actions_behavior == CombinedActionsBehavior.AFTER:
            self.update_joystick_combined_actions(event)

    def handle_events(self):
        end = False
        while not end:
            try:
                event = pygame.event.wait()
                if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                    self.handle_button_event(event)
                elif event.type == pygame.JOYAXISMOTION:
                    self.handle_joystick_event(event)
                elif event.type == pygame.QUIT:
                    end = True
            except KeyError:
                pass
        pygame.quit()

    def quit(self):
        quit_event = pygame.event.Event(pygame.QUIT)
        pygame.event.post(quit_event)
