import XInput
from XInput import *

import pyautogui
pyautogui.PAUSE = 0

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

import math


background_color = "#313335"
text_color = "white"
vertical_deadzone_color = "#52503a"
radial_deadzone_color = "#52503a"

canvas_dimensions = (400, 380)
display_radius = 100
stick_display_radius = 20
outline_width = 4
font_size = 24

#Config
vibration_enabled = False
vertical_deadzone = 0.3
radial_deadzone = 0.6

root = tk.Tk()
root.title("HStickShift")
canvas = tk.Canvas(root, width=canvas_dimensions[0], height=canvas_dimensions[1], bg=background_color)
canvas.pack()

set_deadzone(DEADZONE_TRIGGER, 10)
gears_enabled_global = False

#Display
l_thumb_pos = (canvas_dimensions[0] / 2, canvas_dimensions[1] / 2)

canvas_vertical_deadzone = canvas.create_rectangle(l_thumb_pos[0] - display_radius, l_thumb_pos[1] - vertical_deadzone * display_radius, l_thumb_pos[0] + display_radius, l_thumb_pos[1] + vertical_deadzone * display_radius, width=0, fill=vertical_deadzone_color)
canvas_radial_deadzone = canvas.create_oval(((l_thumb_pos[0] - display_radius * (radial_deadzone), l_thumb_pos[1] - display_radius * (radial_deadzone)), (l_thumb_pos[0] + display_radius * (radial_deadzone), l_thumb_pos[1] + display_radius * (radial_deadzone))), width=0, fill=radial_deadzone_color)

l_thumb_outline = canvas.create_oval(((l_thumb_pos[0] - display_radius, l_thumb_pos[1] - display_radius),
                                      (l_thumb_pos[0] + display_radius, l_thumb_pos[1] + display_radius)), width=outline_width, outline=text_color)

l_thumb_stick_pos = l_thumb_pos

l_thumb_stick = canvas.create_oval(((l_thumb_stick_pos[0] - stick_display_radius, l_thumb_stick_pos[1] - stick_display_radius),
                                         (l_thumb_stick_pos[0] + stick_display_radius, l_thumb_stick_pos[1] + stick_display_radius)), width=outline_width, outline=text_color)

gear_display = canvas.create_text(l_thumb_pos[0], l_thumb_pos[1], fill=text_color, text="", font=("Consolas Bold", font_size))
cur_gear_display = canvas.create_text(l_thumb_pos[0], l_thumb_pos[1], fill=text_color, text="", font=("Consolas Bold", font_size))

colcount_display = canvas.create_text(l_thumb_pos[0], l_thumb_pos[1] - display_radius * 1.5, fill=text_color, text="Press Start", font=("Consolas Bold", font_size))
keys_pressed_display = canvas.create_text(l_thumb_pos[0], l_thumb_pos[1] + display_radius * 1.5, fill=text_color, text="???", font=("Consolas Bold", font_size))


class Controller:
    def __init__(self):

        self.gears_enabled = False
        self.alt_gears = False
        self.keys_currently_pressed = []
        self.column_amount = 4


controllers = (Controller(),
               Controller(),
               Controller(),
               Controller())

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
                controller.column_amount -= 1
                controller.column_amount = max(controller.column_amount, 1)
            elif event.button == "RIGHT_SHOULDER":
                controller.column_amount += 1
                controller.column_amount = min(controller.column_amount, 6)
            elif event.button == "START":
                if not gears_enabled_global:
                    controller.gears_enabled = True
                    gears_enabled_global = True
            elif event.button == "LEFT_THUMB":
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

            #Column definition
            colcount = c.column_amount
            cur_colcount = colcount

            if colcount == 6:
                keys = [
                    [
                        ("1", "num1"), ("3", "num3"), ("5", "num5"), ("7", "num7"), (" ", ""),
                        ("2", "num2"), ("4", "num4"), ("6", "num6"), ("8", "num8"), ("R", "num0")
                    ],
                    [
                        (" 9", "num9"), ("11", "f14"), ("13", "f16"), ("15", "f18"), ("  ", ""),
                        ("10", "f13"), ("12", "f15"), ("14", "f17"), ("16", "f19"), ("R ", "num0")
                    ]
                ]
                cur_colcount = 5
            elif colcount == 5:
                keys = [[
                    ("1", "num1"), ("3", "num3"), ("5", "num5"), ("7", "num7"), ("9", "num9"),
                    ("2", "num2"), ("4", "num4"), ("6", "num6"), ("8", "num8"), ("R", "num0")
                ]]
            if colcount == 4:
                keys = [[
                    ("1", "num1"), ("3", "num3"), ("5", "num5"), ("7", "num7"),
                    ("2", "num2"), ("4", "num4"), ("6", "num6"), ("R", "num0")
                ]]
            elif colcount == 3:
                keys = [[
                    ("1", "num1"), ("3", "num3"), ("5", "num5"),
                    ("2", "num2"), ("4", "num4"), ("R", "num0")
                ]]
            elif colcount == 2:
                keys = [[
                    ("1", "num1"), ("3", "num3"),
                    ("2", "num2"), ("R", "num0")
                ]]
            elif colcount == 1:
                keys = [[
                    ("1", "num1"),
                    ("R", "num0")
                ]]

            colwidth = 2 / cur_colcount

            canvas.itemconfig(cur_gear_display, text="N")
            if colcount == 6:
                canvas.itemconfig(colcount_display, text="<LB  5 columns  RB>" "\n   2 layers (LS)")
            else:
                canvas.itemconfig(colcount_display, text="<LB  " + str(colcount) + " columns  RB>")

            #Choose key set
            selected_keys = keys[c.alt_gears if colcount == 6 else 0]

            #Visual gear display
            txt = ""
            for ii in range(len(selected_keys)):
                txt += selected_keys[ii][0]
                if ii == cur_colcount - 1:
                    txt += "\n\n"
                elif ii < len(selected_keys) - 1:
                    txt += " "
            canvas.itemconfig(gear_display, text=txt)


            #Select gear and change gear display
            gear_selected = -1

            if (stick_pos_y > vertical_deadzone or stick_pos_y < -vertical_deadzone) and math.dist((0, 0), (stick_pos_x, stick_pos_y)) > radial_deadzone:
                i = -1
                col_index = 0
                while i < 1:

                    if stick_pos_x > i and stick_pos_x < i + colwidth:
                        row_offset = cur_colcount if stick_pos_y < 0 else 0
                        gear_selected = selected_keys[col_index + row_offset]

                        canvas.itemconfig(cur_gear_display, text=gear_selected[0])

                    i += colwidth
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
                                time.sleep(0.05)
                                XInput.set_vibration(c_index, 0.0, 0.0)

                            c.keys_currently_pressed.append(k[1])

                    else:
                        if k[1] in c.keys_currently_pressed:

                            pyautogui.keyUp(k[1])
                            #print("stopped pressing", k[1])

                            c.keys_currently_pressed.remove(k[1])

            #Display pressed key
            canvas.itemconfig(keys_pressed_display, text=c.keys_currently_pressed)

        c_index += 1

    try:
        root.update()
    except tk.TclError:
        break
