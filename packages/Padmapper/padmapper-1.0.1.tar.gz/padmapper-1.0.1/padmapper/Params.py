from enum import IntEnum

class CombinedActionsBehavior(IntEnum):
    ONLY = 1
    BEFORE = 2
    AFTER = 3

MOUSE_MOVE_STEP_DEFAULT = 10
MOUSE_HIDE_DELAY_DEFAULT = -1
MOUSE_SWIPE_DIST_DEFAULT = 400
JOYSTICK_COMBINED_ACTIONS_BEHAVIOR_DEFAULT = CombinedActionsBehavior.AFTER


class Params():
    params = {}
    mouse_move_step = MOUSE_MOVE_STEP_DEFAULT
    mouse_hide_delay = MOUSE_HIDE_DELAY_DEFAULT
    mouse_swipe_dist = MOUSE_SWIPE_DIST_DEFAULT
    mouse_move_by_position = False
    joystick_combined_actions_behavior = JOYSTICK_COMBINED_ACTIONS_BEHAVIOR_DEFAULT

    def __init__(self, config):
        if config.get('params') is not None:
            if config['params'].get('mouse_move_step') is not None:
                self.mouse_move_step = config['params']['mouse_move_step']
            if config['params'].get('mouse_hide_delay') is not None:
                self.mouse_hide_delay = config['params']['mouse_hide_delay']
            if config['params'].get('mouse_swipe_dist') is not None:
                self.mouse_swipe_dist = config['params']['mouse_swipe_dist']
            if config['params'].get('mouse_move_by_position') is not None:
                self.mouse_move_by_position = config['params']['mouse_move_by_position']
            if config['params'].get('joystick_combined_actions_behavior') is not None:
                behavior = config['params']['joystick_combined_actions_behavior']
                if behavior == "only":
                    self.joystick_combined_actions_behavior = CombinedActionsBehavior.ONLY
                elif behavior == "before":
                    self.joystick_combined_actions_behavior = CombinedActionsBehavior.BEFORE
                elif behavior == "after":
                    self.joystick_combined_actions_behavior = CombinedActionsBehavior.AFTER
                else:
                    raise "Unknown parameter for joystick combined actions behavior"
