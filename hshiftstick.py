# Imports
import XInput
from XInput import *

import pyautogui
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

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
        gear_mode = 1
    if gear_mode < 1:
        gear_mode = (len(gear_modes) - 1)

def toggle_gear_layer():
    controller.alt_gears = not controller.alt_gears

def toggle_vibration(button):
    global vibration_enabled
    global button_color
    global button_active_color

    vibration_enabled = not vibration_enabled
    button.config(
        text="Vibration: " + ("ON" if vibration_enabled else "OFF"),
        bg=(button_active_color if vibration_enabled else button_color)
    )

def toggle_key_spam_mode(button):
    global key_spam_mode
    global button_color
    global button_active_color

    key_spam_mode = not key_spam_mode
    button.config(
        text="Key Spam: " + ("ON" if key_spam_mode else "OFF"),
        bg=(button_active_color if key_spam_mode else button_color)
    )

def select_button(widget):
    widget['bg'] = 'green'
    widget['activebackground'] = 'green'
    widget['relief'] = 'sunken'

    previously_clicked = widget

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


# START CONFIG ---------------------------------------------------------------------------------------------------------

from configparser import ConfigParser
config = ConfigParser()


if os.path.exists(resource_path("config.ini")):
    config.read('config.ini')
else:
    config.read('config.ini')
    config.add_section('main')

    config.set("main", "cpu_cycle_limit", "0.05") # If over 0, introduces a sleep time (in seconds) inbetween loop cycles

    config.set("main", "vibration_enabled", "1")

    config.set("main", "vertical_deadzone_left", '0.3')
    config.set("main", "vertical_deadzone_right", '0.3')
    config.set("main", "radial_deadzone", "0.6")

    config.set("main", "column_outermargin", "0.1")
    config.set("main", "column_innermargin", "0.001")

    config.set("main", "gear_mode", "4")

    config.set("main", "display_scale", "2")

    config.set("main", "key_spam_mode", "0")

    with open('config.ini', 'w') as f:
        config.write(f)

cpu_cycle_limit = float(config.get("main", "cpu_cycle_limit"))

vibration_enabled = bool(config.get("main", "vibration_enabled"))

vertical_deadzone_left = float(config.get("main", "vertical_deadzone_left"))
vertical_deadzone_right = float(config.get("main", "vertical_deadzone_right"))
radial_deadzone = float(config.get("main", "radial_deadzone"))

column_outermargin = float(config.get("main", "column_outermargin"))
column_innermargin = float(config.get("main", "column_innermargin"))

key_spam_mode = float(config.get("main", "key_spam_mode"))

gear_mode = int(config.get("main", "gear_mode"))

display_scale = int(config.get("main", "display_scale"))

# END CONFIG -----------------------------------------------------------------------------------------------------------


# Gear modes
from gear_modes import *

# Color config
background_color = "#313335"
window_background_color = "#2b2b2b"

column_checkerboard_color = "#3c3f41"
column_checkerboard_color_alt = "#2b2b2b"

text_color = "white"
gear_selected_text = "yellow"

vertical_deadzone_color = "#52503a"
radial_deadzone_color = "#52503a"

button_color = "#3c3f41"
button_active_color = "#547a51"
button_pressed_color = "gray"

# Size config
canvas_dimensions = (260 * display_scale, 200 * display_scale)
display_radius = 50 * display_scale
stick_display_radius = 10 * display_scale
outline_width = 2 * display_scale
margin = 10 * display_scale
font_size = 12 * display_scale
text_font = ("Consolas Bold", font_size)
button_padding = 4 * display_scale
button_margin = 2 * display_scale
button_font = ("Consolas", 5 * display_scale)

# Vibration
vibration_length = 0.15
vibration_strength = (1.0, 0.5)


# Prepare canvas
root = tk.Tk()
root.config(bg=window_background_color)
root.title("HStickShift")
root.iconbitmap(resource_path("icon.ico"))

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

# Gear column checkerboard design
gear_columns = []
for i in range(10):
    gear_columns.append(canvas.create_rectangle(0, 0, 0, 0, width=0,
        fill=column_checkerboard_color if i % 2 == 0 else column_checkerboard_color_alt
    ))

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

l_thumb_stick = canvas.create_oval(
    l_thumb_stick_pos[0] - stick_display_radius, l_thumb_stick_pos[1] - stick_display_radius,
    l_thumb_stick_pos[0] + stick_display_radius, l_thumb_stick_pos[1] + stick_display_radius,
    width=outline_width, outline=text_color
)
l_thumb_stick_cross = canvas.create_text(
    l_thumb_stick_pos[0], l_thumb_stick_pos[1], fill=text_color,
    text="+", font=text_font
)

gear_display = canvas.create_text(
    l_thumb_pos[0], l_thumb_pos[1], fill=text_color,
    text="", font=text_font
)
cur_gear_display = canvas.create_text(
    l_thumb_pos[0], l_thumb_pos[1], fill=gear_selected_text,
    text="", font=text_font
)

mode_display_bg = canvas.create_rectangle(
    0, 0, canvas_dimensions[0], l_thumb_pos[1] - display_radius - margin * 2,
    width=0, fill=window_background_color
)
mode_display = canvas.create_text(
    l_thumb_pos[0], l_thumb_pos[1] - display_radius * 1.5 - margin, fill=text_color,
    text="Press LS / Start", font=text_font
)
keys_pressed_display = canvas.create_text(
    l_thumb_pos[0], l_thumb_pos[1] + display_radius * 1.5, fill=text_color,
    text="", font=text_font
)


# Prepare controllers
class Controller:
    def __init__(self):

        self.gears_enabled = False
        self.alt_gears = False
        self.keys_currently_pressed = []
        self.vibration_countdown = -1


controllers = (
    Controller(),
    Controller(),
    Controller(),
    Controller()
)


# Main loop
while 1:

    # Handle XInput events
    events = get_events()
    for event in events:

        controller = controllers[event.user_index]

        if event.type == EVENT_CONNECTED:
            print("Controller", event.user_index, "connected.")

        elif event.type == EVENT_DISCONNECTED:
            print("Controller", event.user_index, "disconnected.")

        elif event.type == EVENT_STICK_MOVED:
            if event.stick == LEFT:
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
            if event.button in ("DPAD_LEFT", "LEFT_SHOULDER"):
                cycle_gear_mode(-1)
            elif event.button in ("DPAD_RIGHT", "RIGHT_SHOULDER"):
                cycle_gear_mode(1)
            elif event.button in ("START", "LEFT_THUMB"):
                if not gears_enabled_global:

                    # Enable gear functionality
                    controller.gears_enabled = True
                    gears_enabled_global = True
                    gear_controller = controller
                    gear_controller_index = event.user_index

                    # Create buttons
                    widget = tk.Button(None, text='Previous Mode', font=button_font)
                    widget.config(bg=button_color, fg=text_color, highlightthickness=0, borderwidth=0, padx=button_padding, pady=button_padding)
                    widget.config(activebackground=button_pressed_color, activeforeground=text_color)
                    widget.bind('<Button-1>', lambda e: cycle_gear_mode(-1))
                    widget.pack(in_=None, side=tk.LEFT, padx=button_margin, pady=button_margin)

                    widget = tk.Button(None, text='Next Mode', font=button_font)
                    widget.config(bg=button_color, fg=text_color, highlightthickness=0, borderwidth=0, padx=button_padding, pady=button_padding)
                    widget.config(activebackground=button_pressed_color, activeforeground=text_color)
                    widget.bind('<Button-1>', lambda e: cycle_gear_mode(1))
                    widget.pack(in_=None, side=tk.LEFT, padx=button_margin, pady=button_margin)

                    widget = tk.Button(None, text="Vibration: " + ("ON" if vibration_enabled else "OFF"),
                                       font=button_font)
                    widget.config(bg=(button_active_color if vibration_enabled else button_color), fg=text_color, highlightthickness=0, borderwidth=0, padx=button_padding,
                                  pady=button_padding)
                    widget.config(activebackground=button_pressed_color, activeforeground=text_color)
                    widget.bind('<Button-1>', lambda e: toggle_vibration(widget))
                    widget.pack(in_=None, side=tk.RIGHT, padx=button_margin, pady=button_margin)

                    widget = tk.Button(None, text="Key Spam: " + ("ON" if key_spam_mode else "OFF"), font=button_font)
                    widget.config(bg=(button_active_color if key_spam_mode else button_color), fg=text_color, highlightthickness=0, borderwidth=0, padx=button_padding,
                                  pady=button_padding)
                    widget.config(activebackground=button_pressed_color, activeforeground=text_color)
                    widget.bind('<Button-1>', lambda e: toggle_key_spam_mode(widget))
                    widget.pack(in_=None, side=tk.RIGHT, padx=button_margin, pady=button_margin)

                else:
                    toggle_gear_layer()

    # Gear logic
    if gear_controller != -1:
        state = XInput.get_state(gear_controller_index)

        # Stick pos
        stick_pos_x = XInput.get_thumb_values(state)[0][0]
        stick_pos_y = XInput.get_thumb_values(state)[0][1]

        # Choose gear set
        keys = gear_modes[gear_mode][2]
        colcount = gear_modes[gear_mode][1]

        colwidth = (2 - 2 * column_outermargin) / colcount - column_innermargin

        canvas.itemconfig(cur_gear_display, text="N")

        canvas.itemconfig(mode_display, text=gear_modes[gear_mode][0])

        # Choose key set
        selected_keys = keys[gear_controller.alt_gears if len(gear_modes[gear_mode][2]) > 1 else 0]

        # Visual gear display
        txt = ""
        for ii in range(len(selected_keys)):
            txt += selected_keys[ii][0]
            if ii == colcount - 1:
                txt += "\n\n"
            elif ii < len(selected_keys) - 1:
                txt += " "
        canvas.itemconfig(gear_display, text=txt)

        # Gear column checkerboard display
        for i in range(len(gear_columns)):
            canvas.coords(gear_columns[i], 0, 0, 0, 0)

        # Select gear and change gear display
        gear_selected = -1

        if True:
            i = -1 + column_outermargin + column_innermargin / 2
            col_index = 0
            while i < 1 - column_outermargin:

                _range_start = i
                _range_end = i + colwidth

                # Gear column checkerboard display
                canvas.coords(gear_columns[col_index], l_thumb_pos[0] + (_range_start) * display_radius,
                              l_thumb_pos[1] - display_radius,
                              l_thumb_pos[0] + (_range_end) * display_radius,
                              l_thumb_pos[1] + display_radius)

                if not stick_in_deadzone(stick_pos_x, stick_pos_y):
                    if _range_start < stick_pos_x <= _range_end:

                        row_offset = colcount if stick_pos_y < 0 else 0
                        key_candidate = selected_keys[col_index + row_offset]

                        if key_candidate[0] != "":
                            gear_selected = key_candidate
                            canvas.itemconfig(cur_gear_display, text=gear_selected[0])

                i += colwidth + column_innermargin
                col_index += 1

        # Press and unpress keys
        for kc in keys:
            for k in kc:
                if gear_selected != -1 and k[1] == gear_selected[1]:
                    # Start pressing keys
                    if k[1] not in gear_controller.keys_currently_pressed:

                        if not key_spam_mode:
                            pyautogui.keyDown(k[1])
                            # print("started pressing", k[1])
                        gear_controller.keys_currently_pressed.append(k[1])

                        # Vibrate
                        if vibration_enabled:
                            XInput.set_vibration(gear_controller_index, vibration_strength[0], vibration_strength[1])
                            gear_controller.vibration_countdown = time.time()
                    if key_spam_mode:
                        pyautogui.keyDown(k[1])
                        # print("pressed", k[1])
                else:
                    # Stop pressing keys (if pressed)
                    if k[1] in gear_controller.keys_currently_pressed:
                        if not key_spam_mode:
                            pyautogui.keyUp(k[1])
                            # print("stopped pressing", k[1])
                        gear_controller.keys_currently_pressed.remove(k[1])

        # Display pressed key
        canvas.itemconfig(keys_pressed_display,
              text="Pressed: " + " ".join(gear_controller.keys_currently_pressed) if len(
                  gear_controller.keys_currently_pressed) > 0 else "No key pressed"
              )

        # Stop vibration
        if gear_controller.vibration_countdown != -1 and time.time() - gear_controller.vibration_countdown > vibration_length:
            XInput.set_vibration(gear_controller_index, 0.0, 0.0)
            gear_controller.vibration_countdown = -1

    try:
        root.update()
    except tk.TclError:
        break

    if cpu_cycle_limit > 0:
        time.sleep(cpu_cycle_limit)
