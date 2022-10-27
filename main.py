import XInput
from XInput import *

import pyautogui
pyautogui.PAUSE = 0

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk


root = tk.Tk()
root.title("XInput")
canvas = tk.Canvas(root, width=600, height=400, bg="gray")
canvas.pack()

set_deadzone(DEADZONE_TRIGGER, 10)
gears_enabled_global = False

class Controller:
    def __init__(self, center):
        self.center = center

        self.on_indicator_pos = (self.center[0], self.center[1] - 50)

        self.on_indicator = canvas.create_oval(((self.on_indicator_pos[0] - 10, self.on_indicator_pos[1] - 10),
                                                (self.on_indicator_pos[0] + 10, self.on_indicator_pos[1] + 10)))

        self.l_thumb_pos = (self.center[0] - 60, self.center[1] - 20)

        l_thumb_outline = canvas.create_oval(((self.l_thumb_pos[0] - 50, self.l_thumb_pos[1] - 50),
                                              (self.l_thumb_pos[0] + 50, self.l_thumb_pos[1] + 50)))

        l_thumb_stick_pos = self.l_thumb_pos

        self.l_thumb_stick = canvas.create_oval(((l_thumb_stick_pos[0] - 10, l_thumb_stick_pos[1] - 10),
                                                 (l_thumb_stick_pos[0] + 10, l_thumb_stick_pos[1] + 10)))

        self.gears_enabled = False
        self.keys_currently_pressed = []
        self.column_amount = 4

        self.gear_display = canvas.create_text(self.l_thumb_pos[0], self.l_thumb_pos[1], fill="darkblue", text="", font=("Consolas Bold", 12))
        self.cur_gear_display = canvas.create_text(self.l_thumb_pos[0], self.l_thumb_pos[1], fill="darkblue", text="", font=("Consolas Bold", 12))

        self.colcount_display = canvas.create_text(self.l_thumb_pos[0], self.l_thumb_pos[1] - 64, fill="darkblue", text="Press Start", font=("Consolas Bold", 12))
        self.keys_pressed_display = canvas.create_text(self.l_thumb_pos[0], self.l_thumb_pos[1] + 64, fill="darkblue", text="???", font=("Consolas Bold", 12))


controllers = (Controller((150., 100.)),
               Controller((450., 100.)),
               Controller((150., 300.)),
               Controller((450., 300.)))

while 1:
    events = get_events()
    for event in events:
        controller = controllers[event.user_index]
        if event.type == EVENT_CONNECTED:
            canvas.itemconfig(controller.on_indicator, fill="light green")

        elif event.type == EVENT_DISCONNECTED:
            canvas.itemconfig(controller.on_indicator, fill="")

        elif event.type == EVENT_STICK_MOVED:
            if event.stick == LEFT:
                l_thumb_stick_pos = (int(round(controller.l_thumb_pos[0] + 50 * event.x, 0)),
                                     int(round(controller.l_thumb_pos[1] - 50 * event.y, 0)))
                canvas.coords(controller.l_thumb_stick, (
                l_thumb_stick_pos[0] - 10, l_thumb_stick_pos[1] - 10, l_thumb_stick_pos[0] + 10,
                l_thumb_stick_pos[1] + 10))

        elif event.type == EVENT_BUTTON_PRESSED:
            if event.button == "LEFT_SHOULDER":
                controller.column_amount -= 1
            elif event.button == "RIGHT_SHOULDER":
                controller.column_amount += 1
            elif event.button == "START":
                if not gears_enabled_global:
                    controller.gears_enabled = True
                    gears_enabled_global = True

    c_index = 0
    for c in controllers:
        if c.gears_enabled:
            state = XInput.get_state(c_index)

            #Stick pos
            stick_pos_x = XInput.get_thumb_values(state)[0][0]
            stick_pos_y = XInput.get_thumb_values(state)[0][1]

            #Deadzone
            XInput.set_deadzone(DEADZONE_LEFT_THUMB, 15)
            vertical_deadzone = 0.5

            #Column definition
            c.column_amount = min(max(c.column_amount, 1), 5)
            colcount = c.column_amount
            colwidth = 2 / colcount

            if colcount == 5:
                keys = [
                    ("1", "num1"), ("3", "num3"), ("5", "num5"), ("7", "num7"), ("9", "num9"),
                    ("2", "num2"), ("4", "num4"), ("6", "num6"), ("8", "num8"), ("R", "num0")
                ]
            if colcount == 4:
                keys = [
                    ("1", "num1"), ("3", "num3"), ("5", "num5"), ("7", "num7"),
                    ("2", "num2"), ("4", "num4"), ("6", "num6"), ("R", "num0")
                ]
            elif colcount == 3:
                keys = [
                    ("1", "num1"), ("3", "num3"), ("5", "num5"),
                    ("2", "num2"), ("4", "num4"), ("R", "num0")
                ]
            elif colcount == 2:
                keys = [
                    ("1", "num1"), ("3", "num3"),
                    ("2", "num2"), ("R", "num0")
                ]
            elif colcount == 1:
                keys = [
                    ("1", "num1"),
                    ("R", "num0")
                ]

            canvas.itemconfig(c.cur_gear_display, text="N")
            canvas.itemconfig(c.colcount_display, text=str(colcount) + " columns")


            #Visual gear display
            txt = ""
            for ii in range(len(keys)):
                txt += keys[ii][0]
                if ii == colcount - 1:
                    txt += "\n\n"
                elif ii < len(keys) - 1:
                    txt += " "
            canvas.itemconfig(c.gear_display, text=txt)


            #Select gear and change gear display
            gear_selected = -1

            if stick_pos_y > vertical_deadzone or stick_pos_y < -vertical_deadzone:
                i = -1
                col_index = 0
                while i < 1:

                    if stick_pos_x > i and stick_pos_x < i + colwidth:
                        row_offset = colcount if stick_pos_y < 0 else 0
                        gear_selected = keys[col_index + row_offset]

                        canvas.itemconfig(c.cur_gear_display, text=gear_selected[0])

                    i += colwidth
                    col_index += 1


            #Reset all keys but the selected one
            for k in keys:
                if k == gear_selected:
                    if k[1] not in c.keys_currently_pressed:

                        pyautogui.keyDown(k[1])
                        #print("started pressing", k[1])

                        XInput.set_vibration(c_index, 0.5, 0.25)
                        time.sleep(0.05)
                        XInput.set_vibration(c_index, 0.0, 0.0)

                        c.keys_currently_pressed.append(k[1])

                else:
                    if k[1] in c.keys_currently_pressed:

                        pyautogui.keyUp(k[1])
                        #print("stopped pressing", k[1])

                        c.keys_currently_pressed.remove(k[1])

            canvas.itemconfig(c.keys_pressed_display, text=c.keys_currently_pressed)

        c_index += 1

    try:
        root.update()
    except tk.TclError:
        break
