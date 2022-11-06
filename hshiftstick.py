# Imports
import XInput
from XInput import *

import pyautogui
import pydirectinput
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False
pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False
pydirectinput.KEYBOARD_MAPPING['num0'] = 0x52
pydirectinput.KEYBOARD_MAPPING['num1'] = 0x4f
pydirectinput.KEYBOARD_MAPPING['num2'] = 0x50
pydirectinput.KEYBOARD_MAPPING['num3'] = 0x51
pydirectinput.KEYBOARD_MAPPING['num4'] = 0x4b
pydirectinput.KEYBOARD_MAPPING['num5'] = 0x4c
pydirectinput.KEYBOARD_MAPPING['num6'] = 0x4d
pydirectinput.KEYBOARD_MAPPING['num7'] = 0x47
pydirectinput.KEYBOARD_MAPPING['num8'] = 0x48
pydirectinput.KEYBOARD_MAPPING['num9'] = 0x49

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import tkinter.messagebox

vg_available = True
try:
    
    import vgamepad as vg
    gamepad = vg.VX360Gamepad()

    gamepad_buttons = (
        vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
        vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
    )

except:
    print("ViGEmBus not installed.")
    vg_available = False


import math
import time

import sys
import os


# Functions
def stick_in_deadzone(stick_x, stick_y):
    global vertical_deadzone_left
    global vertical_deadzone_right
    global radial_deadzone

    return\
        (stick_x < 0 and stick_y < vertical_deadzone_left and stick_y > -vertical_deadzone_left)\
        or (stick_x >= 0 and stick_y < vertical_deadzone_right and stick_y > -vertical_deadzone_right)\
        or math.dist((0, 0), (stick_x, stick_y)) <= radial_deadzone

def cycle_gear_mode(_dir):
    global gear_mode

    gear_mode += _dir
    if gear_mode > (len(gear_modes) - 1):
        gear_mode = 0
    if gear_mode < 0:
        gear_mode = (len(gear_modes) - 1)

    # Clear custom gear zones
    global user_gear_zones
    user_gear_zones = []

    update_gear_display()

def toggle_gear_layer(controller):
    controller.alt_gears = not controller.alt_gears

    update_gear_display()

def update_gear_display():

    global column_outermargin
    global column_innermargin
    global gear_columns
    global canvas
    global gear_modes
    global gear_controller
    global l_thumb_pos
    global display_radius

    # Update mode title
    mode_display_set("Mode: " + gear_modes[gear_mode][0])

    # Reset display
    for i in range(len(gear_columns)):
        canvas.coords(gear_columns[i][0], 0, 0, 0, 0)

        canvas.coords(gear_columns[i][1], 0, 0)
        canvas.itemconfig(gear_columns[i][1], text="")

    global gear_zones
    gear_zones = []

    for i in canvas_user_gear_zones:
        canvas.coords(
            i[0], -9999, -9999, -9999, -9999
        )
        canvas.coords(
            i[1], -9999, -9999
        )

    if gear_mode == 0:

        # Hide deadzones
        canvas.itemconfig(canvas_vertical_deadzone_left, fill=gear_background_color)
        canvas.itemconfig(canvas_vertical_deadzone_right, fill=gear_background_color)
        canvas.itemconfig(canvas_radial_deadzone, fill=gear_background_color)

        for gz in user_gear_zones:

            _gearname = gz[0]
            _numkey = gz[1]
            _pos_x = gz[2]
            _pos_y = gz[3]
            _range = gz[4]

            canvas.coords(
                canvas_user_gear_zones[int(_numkey.replace("num", ""))][0],
                l_thumb_pos[0] + _pos_x * display_radius - _range * display_radius,
                l_thumb_pos[1] - _pos_y * display_radius - _range * display_radius,
                l_thumb_pos[0] + _pos_x * display_radius + _range * display_radius,
                l_thumb_pos[1] - _pos_y * display_radius + _range * display_radius,
            )

            canvas.coords(
                canvas_user_gear_zones[int(_numkey.replace("num", ""))][1],
                l_thumb_pos[0] + _pos_x * display_radius, l_thumb_pos[1] - _pos_y * display_radius,
            )

    else:

        # Show deadzones
        canvas.itemconfig(canvas_vertical_deadzone_left, fill=vertical_deadzone_color)
        canvas.itemconfig(canvas_vertical_deadzone_right, fill=vertical_deadzone_color)
        canvas.itemconfig(canvas_radial_deadzone, fill=radial_deadzone_color)

        keys = gear_modes[gear_mode][2]
        if gear_controller != -1:
            selected_keys = keys[gear_controller.alt_gears if len(gear_modes[gear_mode][2]) > 1 else 0]
        else:
            selected_keys = keys[0]

        colcount = gear_modes[gear_mode][1]

        _innerarea = 2 - 2 * column_outermargin
        if colcount == 1:
            colwidth = _innerarea
        elif colcount == 2:
            colwidth = (_innerarea - column_innermargin) / colcount
        elif colcount == 3:
            colwidth = (_innerarea - column_innermargin_outer * 2) / colcount
        else:
            colwidth = (_innerarea - column_innermargin_outer * 2 - column_innermargin * (colcount - 1 - 2)) / colcount

        # Define new display
        for row in range(2):
            second_column = row > 0

            i = -1 + column_outermargin
            col_index = 0 + (second_column * colcount)

            while col_index < (len(selected_keys) // 2) * (2 if second_column else 1):

                _range_start = i
                _range_end = i + colwidth
                _range_mid = (_range_start + _range_end) / 2

                # Gear column checkerboard display
                canvas.coords(
                    gear_columns[col_index][0],
                    l_thumb_pos[0] + _range_start * display_radius,
                    l_thumb_pos[1] - display_radius * int(not second_column),
                    l_thumb_pos[0] + _range_end * display_radius,
                    l_thumb_pos[1] + display_radius * int(second_column)
                )
                canvas.itemconfig(
                    gear_columns[col_index][0],
                    fill=column_checkerboard_color if col_index % 2 == (int(second_column) * int(colcount % 2 == 0)) else column_checkerboard_color_alt
                )
                gear_zones.append(
                    (
                        selected_keys[col_index],
                        l_thumb_pos[0] + _range_start * display_radius,
                        l_thumb_pos[1] - display_radius * int(not second_column),
                        l_thumb_pos[0] + _range_end * display_radius,
                        l_thumb_pos[1] + display_radius * int(second_column)
                    )
                )

                numoffset = math.sin((col_index % colcount) / (colcount - 1) * math.pi) if colcount > 1 else 1
                canvas.coords(
                    gear_columns[col_index][1],
                    l_thumb_pos[0] + _range_mid * display_radius,
                    l_thumb_pos[1] + (
                        (display_radius / 2 + numoffset * display_radius / 3)
                        if second_column else
                        (-display_radius / 2 - numoffset * display_radius / 3)
                    )
                )
                canvas.itemconfig(
                    gear_columns[col_index][1],
                    text=selected_keys[col_index][0]
                )

                i += colwidth + (column_innermargin_outer if ((col_index % colcount) in (0, colcount - 2)) and colcount >= 3 else column_innermargin)
                col_index += 1

def toggle_vibration(button):
    global vibration_enabled
    global button_color
    global button_active_color

    vibration_enabled = not vibration_enabled
    button.config(
        bg=(button_active_color if vibration_enabled else button_color)
    )

def toggle_gamepad_emulation(button):

    if not vg_available:
        tk.messagebox.showwarning("ViGEmBus Missing", "ViGEmBus not available - some functionality has been disabled.")
        return

    global gamepad_emulation
    global button_color
    global button_active_color

    gamepad_emulation = not gamepad_emulation
    button.config(
        bg=(button_active_color if gamepad_emulation else button_color)
    )

def toggle_directinput(button):
    global directinput
    global button_color
    global button_active_color

    directinput = not directinput
    button.config(
        bg=(button_active_color if directinput else button_color)
    )

# This function can get temp path for your resource file
# relative_path is your icon file name
# https://stackoverflow.com/questions/71006377/tkinter-icon-is-not-working-after-converting-to-exe
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def key_press(key):
    if directinput:
        pydirectinput.keyDown(key)
    else:
        pyautogui.keyDown(key)

    if vg_available:
        gamepad.press_button(button=gamepad_buttons[int(key.replace("num", ""))])
        gamepad.update()

    # print("started pressing", key)

def key_release(key):
    if directinput:
        pydirectinput.keyUp(key)
    else:
        pyautogui.keyUp(key)

    if vg_available:
        gamepad.release_button(button=gamepad_buttons[int(key.replace("num", ""))])
        gamepad.update()

    # print("stopped pressing", key)

def key_quick_press(key):
    if directinput:
        pydirectinput.press(key)
    else:
        pyautogui.press(key)

    # print("pressed", key


# START CONFIG ---------------------------------------------------------------------------------------------------------

from configparser import ConfigParser
config = ConfigParser()


if os.path.exists("config.ini"):
    config.read('config.ini')
else:
    config.read('config.ini')

    config.add_section("main")
    config.set("main", "gear_mode", "4")
    config.set("main", "display_scale", "2")
    config.set("main", "vibration_enabled", "1")
    config.set("main", "vibration_intensity", "0.5")
    config.set("main", "gamepad_emulation", "0")
    config.set("main", "directinput", "0")

    config.add_section("deadzone")
    config.set("deadzone", "vertical_deadzone_left", '0.3')
    config.set("deadzone", "vertical_deadzone_right", '0.3')
    config.set("deadzone", "radial_deadzone", "0.6")

    config.add_section("margin")
    config.set("margin", "column_outermargin", "0.0")
    config.set("margin", "column_innermargin", "0.0")
    config.set("margin", "column_innermargin_outer", "0.0")

    config.set("main", "cpu_cycle_sleep", "100")

    with open('config.ini', 'w') as f:
        config.write(f)

gear_mode = int(config.get("main", "gear_mode"))
display_scale = int(config.get("main", "display_scale"))
vibration_enabled = config.getboolean("main", "vibration_enabled")
vibration_intensity = float(config.get("main", "vibration_intensity"))
gamepad_emulation = config.getboolean("main", "gamepad_emulation")
if not vg_available:
    gamepad_emulation = False
directinput = config.getboolean("main", "directinput")

vertical_deadzone_left = float(config.get("deadzone", "vertical_deadzone_left"))
vertical_deadzone_right = float(config.get("deadzone", "vertical_deadzone_right"))
radial_deadzone = float(config.get("deadzone", "radial_deadzone"))

column_outermargin = float(config.get("margin", "column_outermargin"))
column_innermargin = float(config.get("margin", "column_innermargin"))
column_innermargin_outer = float(config.get("margin", "column_innermargin_outer"))

# Sleep time (in ms) inbetween loop cycles when not in focus
cpu_cycle_sleep = int(config.get("main", "cpu_cycle_sleep"))

def config_save():

    config.set("main", "gear_mode", str(gear_mode))
    config.set("main", "display_scale", str(display_scale))
    config.set("main", "vibration_enabled", str(vibration_enabled))
    config.set("main", "vibration_intensity", str(vibration_intensity))
    config.set("main", "gamepad_emulation", str(gamepad_emulation))
    config.set("main", "directinput", str(directinput))

    config.set("deadzone", "vertical_deadzone_left", str(vertical_deadzone_left))
    config.set("deadzone", "vertical_deadzone_right", str(vertical_deadzone_right))
    config.set("deadzone", "radial_deadzone", str(radial_deadzone))

    config.set("margin", "column_outermargin", str(column_outermargin))
    config.set("margin", "column_innermargin", str(column_innermargin))
    config.set("margin", "column_innermargin_outer", str(column_innermargin_outer))

    config.set("main", "cpu_cycle_sleep", str(cpu_cycle_sleep))

    with open('config.ini', 'w') as f:
        config.write(f)

# END CONFIG -----------------------------------------------------------------------------------------------------------


# Gear modes
from gear_modes import *
gear_zones = []
user_gear_zones = []

# Color config
from color_config import *

# Size config
canvas_dimensions = (260 * display_scale, 200 * display_scale)
display_radius = 60 * display_scale
stick_display_radius = 10 * display_scale
outline_width = 2 * display_scale
margin = 10 * display_scale
font_size = 12 * display_scale
text_font = ("Consolas Bold", font_size)
button_padding = 4 * display_scale
button_margin = 2 * display_scale
button_font = ("Consolas", 5 * display_scale)
gear_display_font = ("Consolas Bold", 10 * display_scale)
gear_selected_font = ("Consolas Bold", 24 * display_scale)

# Vibration
vibration_length = 0.15

# Prepare canvas
root = tk.Tk()
root.config(bg=gear_background_color)
root.title("HStickShift")
root.iconbitmap(resource_path("icon.ico"))

# Key handling
def onKeyPress(event):
    if event.char in list(map(str, range(10))):
        _numkey = "num" + event.char
        _gearname = event.char if event.char != "0" else "R"
        _range = 0.2

        if _numkey in gear_controller.keys_currently_pressed: # Don't go further if the press is caused by the stick
            return

        if gear_mode == 0 and gears_enabled_global and gear_controller != -1:
            state = XInput.get_state(gear_controller_index)
            stick_pos_x = XInput.get_thumb_values(state)[0][0]
            stick_pos_y = XInput.get_thumb_values(state)[0][1]


            _key_alredy_exists = False
            for i in user_gear_zones:
                if i[1] == _numkey:
                    _key_alredy_exists = True
                    _key_index = user_gear_zones.index(i)
                    break

            if _key_alredy_exists:
                print("Changing location of", _gearname)
                user_gear_zones[_key_index][2] = stick_pos_x
                user_gear_zones[_key_index][3] = stick_pos_y
                user_gear_zones[_key_index][4] = _range
            else:
                print("Setting location of", _gearname)
                user_gear_zones.append(
                    [
                        _gearname,
                        _numkey,
                        stick_pos_x,
                        stick_pos_y,
                        _range
                    ]
                )

            update_gear_display()

root.bind('<KeyPress>', onKeyPress)

# Save config before closing
def root_close():
    config_save()
    root.destroy()
root.wm_protocol("WM_DELETE_WINDOW", root_close)

canvas = tk.Canvas(root, width=canvas_dimensions[0], height=canvas_dimensions[1], bg=background_color)
canvas.config(highlightthickness=0) # Remove outline
canvas.pack()

# Gear controller variables
gears_enabled_global = False
gear_controller = -1
gear_controller_index = -1


# Display
l_thumb_pos = (canvas_dimensions[0] / 2, canvas_dimensions[1] / 2)
l_thumb_stick_pos = l_thumb_pos

# Background
l_thumb_outline = canvas.create_rectangle(
    l_thumb_pos[0] - display_radius, l_thumb_pos[1] - display_radius,
    l_thumb_pos[0] + display_radius, l_thumb_pos[1] + display_radius,
    width=0, fill=gear_background_color
)

# Gear column checkerboard design
gear_columns = []
for i in range(10 * 2):
    gear_columns.append(
        [
            canvas.create_rectangle(
                0, 0, 0, 0, width=0,
            )
        ]
    )

# Deadzones
canvas_vertical_deadzone_left = canvas.create_rectangle(
    l_thumb_pos[0] - display_radius, l_thumb_pos[1] - vertical_deadzone_left * display_radius,
    l_thumb_pos[0], l_thumb_pos[1] + vertical_deadzone_left * display_radius,
    width=0, fill=vertical_deadzone_color
)
canvas_vertical_deadzone_right = canvas.create_rectangle(
    l_thumb_pos[0], l_thumb_pos[1] - vertical_deadzone_right * display_radius,
    l_thumb_pos[0] + display_radius, l_thumb_pos[1] + vertical_deadzone_right * display_radius,
    width=0, fill=vertical_deadzone_color
)
canvas_radial_deadzone = canvas.create_oval(
    l_thumb_pos[0] - display_radius * radial_deadzone, l_thumb_pos[1] - display_radius * radial_deadzone,
    l_thumb_pos[0] + display_radius * radial_deadzone, l_thumb_pos[1] + display_radius * radial_deadzone,
    width=0, fill=radial_deadzone_color
)

# Gear column text
for i in range(10 * 2):
    gear_columns[i].append(
        canvas.create_text(
            0, 0, fill=text_color,
            text="", font=gear_display_font
        )
    )

# Big circle to mask checkerboard and deadzone
canvas.create_oval(
    l_thumb_pos[0] - display_radius * 2, l_thumb_pos[1] - display_radius * 2,
    l_thumb_pos[0] + display_radius * 2, l_thumb_pos[1] + display_radius * 2,
    width=display_radius * 2, outline=background_color
)

l_thumb_outline = canvas.create_oval(
    l_thumb_pos[0] - display_radius, l_thumb_pos[1] - display_radius,
    l_thumb_pos[0] + display_radius, l_thumb_pos[1] + display_radius,
    width=outline_width, outline=text_color
)

# User defined gear zones
canvas_user_gear_zones = []
for i in range(10):
    canvas_user_gear_zones.append(
        [
            canvas.create_oval(
                -9999, -9999, -9999, -9999,
                fill=column_checkerboard_color, width=0
            ),
        ]
    )
for i in range(10):
    canvas_user_gear_zones[i].append(
        canvas.create_text(
            -9999, -9999,
            text=str(i) if i != 0 else "R", fill=text_color, font=gear_display_font
        )
    )

cur_gear_display = canvas.create_text(
    l_thumb_pos[0], l_thumb_pos[1], fill=gear_selected_text,
    text="N", font=gear_selected_font
)

l_thumb_stick = canvas.create_oval(
    -9999, -9999, -9999, -9999,
    width=outline_width, outline=text_color
)
l_thumb_stick_cross = canvas.create_text(
    -9999, -9999, fill=text_color,
    text="+", font=text_font
)

# Mode display
mode_display_bg = canvas.create_rectangle(
    0, 0, canvas_dimensions[0], margin * 3,
    width=0, fill=window_background_color
)
mode_display = canvas.create_text(
    l_thumb_pos[0], margin * 1.5, fill=text_color,
    text="", font=text_font
)
def mode_display_set(_text="Mode Display Text"):
    canvas.itemconfig(mode_display, text=_text)
mode_display_set()

# Status bar
keys_pressed_display_bg = canvas.create_rectangle(
    0, canvas_dimensions[1] - margin * 3, canvas_dimensions[0], canvas_dimensions[1],
    width=0, fill=window_background_color
)
keys_pressed_display = canvas.create_text(
    l_thumb_pos[0], canvas_dimensions[1] - margin * 1.5, fill=text_color,
    text="", font=text_font
)
def status_bar_set(_text="Press LS / Start"):
    canvas.itemconfig(keys_pressed_display, text=_text)
status_bar_set()

# Create buttons
widget = tk.Button(None, text='Prev Mode', font=button_font)
widget.config(bg=button_color, fg=text_color, highlightthickness=0, borderwidth=0, padx=button_padding, pady=button_padding)
widget.config(activebackground=button_pressed_color, activeforeground=text_color)
widget.bind('<Button-1>', lambda e: cycle_gear_mode(-1))
widget.pack(in_=None, side=tk.LEFT, padx=button_margin, pady=button_margin)

widget = tk.Button(None, text='Next Mode', font=button_font)
widget.config(bg=button_color, fg=text_color, highlightthickness=0, borderwidth=0, padx=button_padding, pady=button_padding)
widget.config(activebackground=button_pressed_color, activeforeground=text_color)
widget.bind('<Button-1>', lambda e: cycle_gear_mode(1))
widget.pack(in_=None, side=tk.LEFT, padx=button_margin, pady=button_margin)

widget = tk.Button(None, text="Vibration",
                   font=button_font)
widget.config(bg=(button_active_color if vibration_enabled else button_color), fg=text_color, highlightthickness=0, borderwidth=0, padx=button_padding,
              pady=button_padding)
widget.config(activebackground=button_pressed_color, activeforeground=text_color)
widget.bind('<Button-1>', lambda e: toggle_vibration(widget))
widget.pack(in_=None, side=tk.RIGHT, padx=button_margin, pady=button_margin)

widget2 = tk.Button(None, text="Gamepad", font=button_font)
widget2.config(bg=(button_active_color if gamepad_emulation else button_color), fg=text_color, highlightthickness=0, borderwidth=0, padx=button_padding,
              pady=button_padding, state=(tk.NORMAL if vg_available else tk.DISABLED))
widget2.config(activebackground=button_pressed_color, activeforeground=text_color)
widget2.bind('<Button-1>', lambda e: toggle_gamepad_emulation(widget2))
widget2.pack(in_=None, side=tk.RIGHT, padx=button_margin, pady=button_margin)

widget3 = tk.Button(None, text="Direct Input", font=button_font)
widget3.config(bg=(button_active_color if directinput else button_color), fg=text_color, highlightthickness=0, borderwidth=0, padx=button_padding,
              pady=button_padding)
widget3.config(activebackground=button_pressed_color, activeforeground=text_color)
widget3.bind('<Button-1>', lambda e: toggle_directinput(widget3))
widget3.pack(in_=None, side=tk.RIGHT, padx=button_margin, pady=button_margin)


def change_radial_deadzone(e):
    global radial_deadzone
    radial_deadzone = radial_deadzone_slider.get()

    canvas.coords(
        canvas_radial_deadzone,
        l_thumb_pos[0] - display_radius * radial_deadzone, l_thumb_pos[1] - display_radius * radial_deadzone,
        l_thumb_pos[0] + display_radius * radial_deadzone, l_thumb_pos[1] + display_radius * radial_deadzone,
    )

radial_deadzone_slider = tk.Scale(None, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, digits=3, command=change_radial_deadzone)
radial_deadzone_slider.config(
    bg=button_color, fg=text_color, highlightthickness=0, borderwidth=0, troughcolor=radial_deadzone_color, label="Radial Deadzone"
)
radial_deadzone_slider.set(radial_deadzone)
canvas.create_window(margin * 0.5, margin * 3.5, anchor=tk.NW, window=radial_deadzone_slider)


def change_vertical_deadzone_left(e):
    global vertical_deadzone_left
    vertical_deadzone_left = vertical_deadzone_left_slider.get()

    canvas.coords(
        canvas_vertical_deadzone_left,
        l_thumb_pos[0] - display_radius, l_thumb_pos[1] - vertical_deadzone_left * display_radius,
        l_thumb_pos[0], l_thumb_pos[1] + vertical_deadzone_left * display_radius,
    )

vertical_deadzone_left_slider = tk.Scale(None, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, digits=3, command=change_vertical_deadzone_left)
vertical_deadzone_left_slider.config(
    bg=button_color, fg=text_color, highlightthickness=0, borderwidth=0, troughcolor=vertical_deadzone_color, label="Left Deadzone"
)
vertical_deadzone_left_slider.set(vertical_deadzone_left)
canvas.create_window(margin * 0.5, margin * (3.5 + 3), anchor=tk.NW, window=vertical_deadzone_left_slider)


def change_vertical_deadzone_right(e):
    global vertical_deadzone_right
    vertical_deadzone_right = vertical_deadzone_right_slider.get()

    canvas.coords(
        canvas_vertical_deadzone_right,
        l_thumb_pos[0], l_thumb_pos[1] - vertical_deadzone_right * display_radius,
                        l_thumb_pos[0] + display_radius, l_thumb_pos[1] + vertical_deadzone_right * display_radius,
    )

vertical_deadzone_right_slider = tk.Scale(None, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, digits=3, command=change_vertical_deadzone_right)
vertical_deadzone_right_slider.config(
    bg=button_color, fg=text_color, highlightthickness=0, borderwidth=0, troughcolor=vertical_deadzone_color, label="Right Deadzone"
)
vertical_deadzone_right_slider.set(vertical_deadzone_right)
canvas.create_window(margin * 0.5, margin * (3.5 + 6), anchor=tk.NW, window=vertical_deadzone_right_slider)


def change_cpu_cycle_sleep(e):
    global cpu_cycle_sleep
    cpu_cycle_sleep = cpu_cycle_sleep_slider.get()

cpu_cycle_sleep_slider = tk.Scale(None, from_=1, to=200, resolution=1, orient=tk.HORIZONTAL, command=change_cpu_cycle_sleep)
cpu_cycle_sleep_slider.config(
    bg=button_color, fg=text_color, highlightthickness=0, borderwidth=0, troughcolor=gear_background_color, label="CPU Sleep"
)
cpu_cycle_sleep_slider.set(cpu_cycle_sleep)
canvas.create_window(margin * 0.5, canvas_dimensions[1] - margin * (3.5), anchor=tk.SW, window=cpu_cycle_sleep_slider)


def change_vibration_intensity(e):
    global vibration_intensity
    vibration_intensity = vibration_intensity_slider.get()

vibration_intensity_slider = tk.Scale(None, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, digits=3, command=change_vibration_intensity)
vibration_intensity_slider.config(
    bg=button_color, fg=text_color, highlightthickness=0, borderwidth=0, troughcolor=button_active_color, label="Vibration Intensity"
)
vibration_intensity_slider.set(vibration_intensity)
canvas.create_window(canvas_dimensions[0] - margin * 0.5, margin * (3.5), anchor=tk.NE, window=vibration_intensity_slider)


def change_column_outermargin(e):
    global column_outermargin
    column_outermargin = column_outermargin_slider.get()
    update_gear_display()

column_outermargin_slider = tk.Scale(None, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, digits=3, command=change_column_outermargin)
column_outermargin_slider.config(
    bg=button_color, fg=text_color, highlightthickness=0, borderwidth=0, troughcolor=gear_background_color, label="Outer Margin"
)
column_outermargin_slider.set(column_outermargin)
canvas.create_window(canvas_dimensions[0] - margin * 0.5, canvas_dimensions[1] - margin * (3.5 + 6), anchor=tk.SE, window=column_outermargin_slider)

def change_column_innermargin(e):
    global column_innermargin
    column_innermargin = column_innermargin_slider.get()
    update_gear_display()

column_innermargin_slider = tk.Scale(None, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, digits=3, command=change_column_innermargin)
column_innermargin_slider.config(
    bg=button_color, fg=text_color, highlightthickness=0, borderwidth=0, troughcolor=gear_background_color, label="Inner Margin"
)
column_innermargin_slider.set(column_innermargin)
canvas.create_window(canvas_dimensions[0] - margin * 0.5, canvas_dimensions[1] - margin * (3.5 + 3), anchor=tk.SE, window=column_innermargin_slider)

def change_column_innermargin_outer(e):
    global column_innermargin_outer
    column_innermargin_outer = column_innermargin_outer_slider.get()
    update_gear_display()

column_innermargin_outer_slider = tk.Scale(None, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, digits=3, command=change_column_innermargin_outer)
column_innermargin_outer_slider.config(
    bg=button_color, fg=text_color, highlightthickness=0, borderwidth=0, troughcolor=gear_background_color, label="Inouter Margin"
)
column_innermargin_outer_slider.set(column_innermargin_outer)
canvas.create_window(canvas_dimensions[0] - margin * 0.5, canvas_dimensions[1] - margin * (3.5 + 0), anchor=tk.SE, window=column_innermargin_outer_slider)

# Update gear display initially
update_gear_display()

# Prepare controllers
class Controller:
    def __init__(self):

        self.gears_enabled = False
        self.alt_gears = False
        self.keys_currently_pressed = []
        self.vibration_countdown = -1
        self.gear_stick = -1


controllers = (
    Controller(),
    Controller(),
    Controller(),
    Controller()
)


# Main loop
def main_loop():

    global gear_controller
    global gears_enabled_global
    global gear_controller_index

    # Handle XInput events
    events = get_events()
    for event in events:

        controller = controllers[event.user_index]

        if event.type == EVENT_CONNECTED:
            print("Controller", event.user_index, "connected.")

        elif event.type == EVENT_DISCONNECTED:
            print("Controller", event.user_index, "disconnected.")

            if controller == gear_controller:

                controller.gears_enabled = False
                gears_enabled_global = False
                gear_controller = -1
                gear_controller_index = -1
                controller.gear_stick = -1

                status_bar_set()

        elif event.type == EVENT_STICK_MOVED:

            if controller == gear_controller:
                if event.stick == controller.gear_stick:
                    if controller.gears_enabled:
                        l_thumb_stick_pos = (
                            int(round(l_thumb_pos[0] + display_radius * event.x, 0)),
                            int(round(l_thumb_pos[1] - display_radius * event.y, 0))
                        )
                        canvas.coords(l_thumb_stick, (
                            l_thumb_stick_pos[0] - stick_display_radius, l_thumb_stick_pos[1] - stick_display_radius,
                            l_thumb_stick_pos[0] + stick_display_radius, l_thumb_stick_pos[1] + stick_display_radius
                        ))
                        canvas.coords(l_thumb_stick_cross, (
                            l_thumb_stick_pos[0], l_thumb_stick_pos[1],
                        ))


        elif event.type == EVENT_BUTTON_PRESSED:

            if event.button in ("LEFT_THUMB", "RIGHT_THUMB"):
                if not gears_enabled_global:

                    # Enable gear functionality
                    controller.gears_enabled = True
                    gears_enabled_global = True
                    gear_controller = controller
                    gear_controller_index = event.user_index
                    controller.gear_stick = LEFT if event.button == "LEFT_THUMB" else RIGHT

                    # Update gear display
                    update_gear_display()

                elif controller == gear_controller:
                    toggle_gear_layer(controller)

    # Gear logic
    if gear_controller != -1:

        # Stick pos
        state = XInput.get_state(gear_controller_index)
        stick_pos_x = XInput.get_thumb_values(state)[0 if gear_controller.gear_stick == LEFT else 1][0]
        stick_pos_y = XInput.get_thumb_values(state)[0 if gear_controller.gear_stick == LEFT else 1][1]
        # print("Stick pos: ", stick_pos_x, stick_pos_y)

        canvas.itemconfig(cur_gear_display, text="N")


        if gear_mode == 0:

            gear_selected = -1

            for gz in user_gear_zones:

                _gearname = gz[0]
                _numkey = gz[1]
                _x = gz[2]
                _y = gz[3]
                _range = gz[4]

                if math.dist((stick_pos_x, stick_pos_y), (_x, _y)) <= _range:
                    gear_selected = _numkey
                    canvas.itemconfig(cur_gear_display, text=_gearname)

            # Press and unpress keys
            for k in list(map(lambda x: "num" + str(x), range(10))):
                if gear_selected != -1 and k == gear_selected:
                    # Start pressing keys
                    if k not in gear_controller.keys_currently_pressed:

                        key_press(k)
                        gear_controller.keys_currently_pressed.append(k)

                        # Vibrate
                        if vibration_enabled:
                            XInput.set_vibration(gear_controller_index, vibration_intensity,
                                                 vibration_intensity)
                            gear_controller.vibration_countdown = time.time()
                else:
                    # Stop pressing keys (if pressed)
                    if k in gear_controller.keys_currently_pressed:
                        key_release(k)
                        gear_controller.keys_currently_pressed.remove(k)



        else:

            gear_selected = -1

            if not stick_in_deadzone(stick_pos_x, stick_pos_y):
                for gz in gear_zones:

                    _key = gz[0]
                    _x1 = gz[1]
                    _y1 = gz[2]
                    _x2 = gz[3]
                    _y2 = gz[4]

                    if _x1 < (l_thumb_pos[0] + stick_pos_x * display_radius) <= _x2\
                        and stick_pos_y != 0 and _y1 <= (l_thumb_pos[1] - stick_pos_y * display_radius) <= _y2:

                        key_candidate = _key
                        if key_candidate[0] != "":
                            gear_selected = key_candidate
                            canvas.itemconfig(cur_gear_display, text=gear_selected[0])

            # Press and unpress keys
            keys = gear_modes[gear_mode][2]
            for kc in keys:
                for k in kc:
                    if gear_selected != -1 and k[1] == gear_selected[1]:
                        # Start pressing keys
                        if k[1] not in gear_controller.keys_currently_pressed:

                            key_press(k[1])
                            gear_controller.keys_currently_pressed.append(k[1])

                            # Vibrate
                            if vibration_enabled:
                                XInput.set_vibration(gear_controller_index, vibration_intensity, vibration_intensity)
                                gear_controller.vibration_countdown = time.time()
                    else:
                        # Stop pressing keys (if pressed)
                        if k[1] in gear_controller.keys_currently_pressed:
                            key_release(k[1])
                            gear_controller.keys_currently_pressed.remove(k[1])

        # Display pressed key
        status_bar_set(
            "Pressed: " + " ".join(gear_controller.keys_currently_pressed)
            if len(gear_controller.keys_currently_pressed) > 0
            else "No key pressed"
        )

        # Stop vibration
        if gear_controller.vibration_countdown != -1 and time.time() - gear_controller.vibration_countdown > vibration_length:
            XInput.set_vibration(gear_controller_index, 0.0, 0.0)
            gear_controller.vibration_countdown = -1

    root.after(1 if root.focus_displayof() else cpu_cycle_sleep, main_loop)

root.after(1, main_loop)
root.mainloop()