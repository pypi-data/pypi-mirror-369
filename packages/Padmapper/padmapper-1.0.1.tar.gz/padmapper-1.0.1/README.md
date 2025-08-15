# Padmapper - Add gamepad support to Linux games that only support keyboard and/or mouse !

Padmapper is a Linux tool which simulates keyboard and mouse from game
controller inputs.
So you can press keyboard keys through gamepad buttons, and move mouse cursor
using a joystick.

## Installation

X.Org is required, Padmapper is not working with Wayland at this time.

### Using pip

```
pip install padmapper
```

### Using Make

Python dependencies:

- pynput
- pygame

```
sudo make install
```

## Write games config file

In the `configs` folder, you have Padmapper example configuration files for
some games. Those files car help you to write your own.

### Config file format

The file is formatted as JSON. Please refer to `config_template.json` to
discover the basic file structure with the default options values.

In this template file, you can see the root element is a dictionary which
contains:

- a `params` section, which stands for [global settings](#global-settings),
- an empty entry for a single gamepad controller, identified by index `0`.

#### Global settings

Global settings are to be set in `params` entry in the root dictionary.
The value is a dictionary which accepts these optional parameters:

- `mouse_hide_delay`, in seconds (default: -1, disabled),
- `mouse_move_step`, to adjust according to the game (default: 10),
- `mouse_swipe_dist`, to adjust according to the game (default: 400),
- `mouse_move_by_position`, set to true for absolute positioning, else relative
  positioning (default: false),
- `joystick_combined_actions_behavior`, configure how to handle multiple axis
  triggered at the same time, see [joystick](#joystick) (default: "after").

#### Gamepads settings

You can add as gamepads entries as needed in the root dictionary. Gamepad
entries are identified by integers, values are starting from 0 and are
contiguous.

Each gamepad entry is a dictionary which accept the following sections:
- `buttons`: to configure gamepad [buttons](#buttons) actions,
- `joystick`: to configure [joystick](#joystick) actions.

##### Buttons

The `buttons` dictionary is inside the [gamepad
dictionary](#gamepads-settings).
It defines the button identifier (integer) and an array for the actions to do
when pressed.
Use `padmapper-capture` to find buttons identifiers.

In this array you can list keyboard keypresses or mouse events associated to
the button. Several actions can be listed in this array.
See [Actions](#actions) to know what you can do.

##### Joystick

The `joystick` dictionary is inside the [gamepad
dictionary](#gamepads-settings).
It defines the actions to do according to the triggered axis, "0" or "1"
(vertical or horizontal), and the position, "-1" or "1" (left, right, top,
down).
Use `padmapper-capture` to know how left, right, top, bottom are represented.

Moreover, you can define combined actions, for the case or two axis are
triggered at the same time. To do this, you have a `combined` entry in the
`joystick` dictionary, which accepts "-1:-1", "-1:1", "1:-1", "1:1" for the two
axis positions.
Joystick actions are affected by the `joystick_combined_actions_behavior`
[global setting](#global-settings), which accept the following values:

- "only": if combined actions are triggered, do not perform single axis
  associated actions,
- "before": do combined actions before single axis associated actions,
- "after": do combined actions after single axis associated actions.

Finally, you can define an "ignore" entry in `joystick` dictionary, with array
as value, if you want to ignore some of your joystick axis.

See [Actions](#actions) to know what you can do.

##### Actions

The actions are always put in an array, even if there is a single action.

Actions can be a keyboard keypress. You can see the list of the keys values to
use
[from pyinput documentation](https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key).
You can use keys characters (letters, digits, ...).

You can also list mouse actions by using as value a dictionary:

```json
[{"mouse": []
```
and the associated array takes an action to perform on the pointer:
- "click", "rclick", left or right click,
- "dbclick", "rdbclick", for left or right double click,
- "hold", "rhold", to hold left or right button,
- "up", "down", "left", "right",
- "left_up", "left_right", "right_up", "right_down",
- "swipe_up", "swipe_down", "swipe_left", "swipe_right",
- "swipe_left_up", "swipe_left_down", "swipe_right_up", "swipe_right_down",
- "hide", to hide the cursor.

Mouse moves are affected by the `mouse_move_by_position` [global
setting](#global-settings), which moves cursor relatively or absolutely.

## Use Padmapper

To use Padmapper with a game, run the Padmapper launcher, by providing the
Padmapper game config file, the game binary, and the game parameters:

```
padmapper config.json game.bin ...
```

## Get gamepad buttons identifiers

To get gamepad buttons identifiers, and axis behavior, you can use
`padmapper-capture`.

But as an alternative, there is `jstest`.
To install it, on Ubuntu/Debian:

```
sudo apt install joystick
```

on ArchLinux:

```
sudo pacman -S joyutils
```

And just run it with:

```
jstest /dev/input/js0
```


