# START CONFIG ---------------------------------------------------------------------------------------------------------

# Color config
background_color = "#313335"

column_checkerboard_color = "#3c3f41"
column_checkerboard_color_alt = "#2b2b2b"

text_color = "white"
gear_selected_text = "yellow"

vertical_deadzone_color = "#52503a"
radial_deadzone_color = "#52503a"

#Size config
display_scale = 2
canvas_dimensions = (240 * display_scale, 200 * display_scale)
display_radius = 50 * display_scale
stick_display_radius = 10 * display_scale
outline_width = 2 * display_scale
font_size = 12 * display_scale

#Config
vibration_enabled = True
vibration_length = 0.1

vertical_deadzone = 0.3
radial_deadzone = 0.6

column_outermargin = 0.10
column_innermargin = 0.05

# Gear modes
starting_gear_mode = 4
gear_modes = [
    (
        "0 Gears",  # Name
        0,          # Column count
        (
            (),
        )        # Gears
    ),
    (
        "1 Gear",
        1,
        (
            (
                ("1", "num1"),
                ("R", "num0")
            ),
        )
    ),
    (
        "3 Gears",
        2,
        (
            (
                ("1", "num1"), ("3", "num3"),
                ("2", "num2"), ("R", "num0")
            ),
        )
    ),
    (
        "5 Gears",
        3,
        (
            (
                ("1", "num1"), ("3", "num3"), ("5", "num5"),
                ("2", "num2"), ("4", "num4"), ("R", "num0")
            ),
        )
    ),
    (
        "7 Gears",
        4,
        (
            (
                ("1", "num1"), ("3", "num3"), ("5", "num5"), ("7", "num7"),
                ("2", "num2"), ("4", "num4"), ("6", "num6"), ("R", "num0")
            ),
        )
    ),
    (
        "9 Gears",
        5,
        (
            (
                ("1", "num1"), ("3", "num3"), ("5", "num5"), ("7", "num7"), ("9", "num9"),
                ("2", "num2"), ("4", "num4"), ("6", "num6"), ("8", "num8"), ("R", "num0")
            ),
        )
    ),
    (
        "16 Gears (2 Layers - LS)",
        5,
        (
            (
                ("1", "num1"), ("3", "num3"), ("5", "num5"), ("7", "num7"), ("", ""),
                ("2", "num2"), ("4", "num4"), ("6", "num6"), ("8", "num8"), ("R", "num0")
            ),
            (
                (" 9", "num9"), ("11", "f14"), ("13", "f16"), ("15", "f18"), ("", ""),
                ("10", "f13"), ("12", "f15"), ("14", "f17"), ("16", "f19"), ("R ", "num0")
            ),
        )
    )
]

# END CONFIG -----------------------------------------------------------------------------------------------------------


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


# Prepare canvas
root = tk.Tk()
root.title("HStickShift")
canvas = tk.Canvas(root, width=canvas_dimensions[0], height=canvas_dimensions[1], bg=background_color)
canvas.pack()


# Variable that makes it so that only one controller can have gear functionality
gears_enabled_global = False


# Display
l_thumb_pos = (canvas_dimensions[0] / 2, canvas_dimensions[1] / 2)
l_thumb_stick_pos = l_thumb_pos

# Gear column checkerbox design
gear_columns = []
for i in range(10):
    gear_columns.append(canvas.create_rectangle(0, 0, 0, 0, width=0, fill=column_checkerboard_color if i % 2 == 0 else column_checkerboard_color_alt))

canvas_vertical_deadzone = canvas.create_rectangle(
    l_thumb_pos[0] - display_radius, l_thumb_pos[1] - vertical_deadzone * display_radius,
    l_thumb_pos[0] + display_radius, l_thumb_pos[1] + vertical_deadzone * display_radius,
    width=0, fill=vertical_deadzone_color
)
canvas_radial_deadzone = canvas.create_oval(
    l_thumb_pos[0] - display_radius * radial_deadzone, l_thumb_pos[1] - display_radius * radial_deadzone,
    l_thumb_pos[0] + display_radius * radial_deadzone, l_thumb_pos[1] + display_radius * radial_deadzone,
    width=0, fill=radial_deadzone_color
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

gear_display = canvas.create_text(
    l_thumb_pos[0], l_thumb_pos[1], fill=text_color,
    text="", font=("Consolas Bold", font_size)
)
cur_gear_display = canvas.create_text(
    l_thumb_pos[0], l_thumb_pos[1], fill=gear_selected_text,
    text="", font=("Consolas Bold", font_size)
)

colcount_display = canvas.create_text(
    l_thumb_pos[0], l_thumb_pos[1] - display_radius * 1.5, fill=text_color,
    text="Press Start", font=("Consolas Bold", font_size)
)
keys_pressed_display = canvas.create_text(
    l_thumb_pos[0], l_thumb_pos[1] + display_radius * 1.5, fill=text_color,
    text="", font=("Consolas Bold", font_size)
)


# Prepare controllers
class Controller:
    def __init__(self):

        self.gears_enabled = False
        self.alt_gears = False
        self.keys_currently_pressed = []
        self.gear_mode = starting_gear_mode


controllers = (
    Controller(),
    Controller(),
    Controller(),
    Controller()
)


# Main loop
while 1:
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
                    l_thumb_stick_pos = (int(round(l_thumb_pos[0] + display_radius * event.x, 0)),
                                         int(round(l_thumb_pos[1] - display_radius * event.y, 0)))
                    canvas.coords(l_thumb_stick, (
                    l_thumb_stick_pos[0] - stick_display_radius, l_thumb_stick_pos[1] - stick_display_radius, l_thumb_stick_pos[0] + stick_display_radius,
                    l_thumb_stick_pos[1] + stick_display_radius))

        elif event.type == EVENT_BUTTON_PRESSED:
            if event.button == "LEFT_SHOULDER":
                controller.gear_mode -= 1
                controller.gear_mode = max(controller.gear_mode, 1)
            elif event.button == "RIGHT_SHOULDER":
                controller.gear_mode += 1
                controller.gear_mode = min(controller.gear_mode, 6)
            elif event.button == "START":
                if not gears_enabled_global:
                    controller.gears_enabled = True
                    gears_enabled_global = True
            elif event.button == "LEFT_THUMB":
                if not gears_enabled_global:
                    controller.gears_enabled = True
                    gears_enabled_global = True
                else :
                    controller.alt_gears = not controller.alt_gears

    c_index = 0
    for c in controllers:
        if c.gears_enabled:
            state = XInput.get_state(c_index)

            #Stick pos
            stick_pos_x = XInput.get_thumb_values(state)[0][0]
            stick_pos_y = XInput.get_thumb_values(state)[0][1]

            #Deadzone
            XInput.set_deadzone(DEADZONE_LEFT_THUMB, 0)
            vertical_deadzone = vertical_deadzone

            # Choose gear set
            keys = gear_modes[c.gear_mode][2]
            cur_colcount = gear_modes[c.gear_mode][1]

            colwidth = (2 - 2 * column_outermargin) / cur_colcount - column_innermargin

            canvas.itemconfig(cur_gear_display, text="N")

            canvas.itemconfig(colcount_display, text="<LB   " + gear_modes[c.gear_mode][0] + "   RB>")

            #Choose key set
            selected_keys = keys[c.alt_gears if c.gear_mode == 6 else 0]

            #Visual gear display
            txt = ""
            for ii in range(len(selected_keys)):
                txt += selected_keys[ii][0]
                if ii == cur_colcount - 1:
                    txt += "\n\n"
                elif ii < len(selected_keys) - 1:
                    txt += " "
            canvas.itemconfig(gear_display, text=txt)

            # Gear column checkerboard display
            for i in range(len(gear_columns)):
                canvas.coords(gear_columns[i], 0, 0, 0, 0)


            #Select gear and change gear display
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

                    if (stick_pos_y > vertical_deadzone or stick_pos_y < -vertical_deadzone) and math.dist((0, 0), (stick_pos_x, stick_pos_y)) > radial_deadzone:
                        if stick_pos_x > _range_start and stick_pos_x < _range_end:

                            row_offset = cur_colcount if stick_pos_y < 0 else 0
                            key_candidate = selected_keys[col_index + row_offset]

                            if key_candidate[0] != "":
                                gear_selected = key_candidate
                                canvas.itemconfig(cur_gear_display, text=gear_selected[0])

                    i += colwidth + column_innermargin
                    col_index += 1


            #Reset all keys but the selected one
            for kc in keys:
                for k in kc:
                    if gear_selected != -1 and k[1] == gear_selected[1]:
                        if k[1] not in c.keys_currently_pressed:

                            pyautogui.keyDown(k[1])
                            #print("started pressing", k[1])

                            if vibration_enabled:
                                XInput.set_vibration(c_index, 0.5, 0.25)
                                time.sleep(vibration_length)
                                XInput.set_vibration(c_index, 0.0, 0.0)

                            c.keys_currently_pressed.append(k[1])

                    else:
                        if k[1] in c.keys_currently_pressed:

                            pyautogui.keyUp(k[1])
                            #print("stopped pressing", k[1])

                            c.keys_currently_pressed.remove(k[1])

            #Display pressed key
            canvas.itemconfig(keys_pressed_display, text=" ".join(c.keys_currently_pressed))

        c_index += 1

    try:
        root.update()
    except tk.TclError:
        break
