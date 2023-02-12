# RaspberryPi Pico Macroboard

import time
import board
from digitalio import DigitalInOut, Direction, Pull
import usb_hid
import rotaryio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

print("---Pico Pad Keyboard---")

led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
#led.value = True

kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)
kbdl = KeyboardLayoutUS(kbd)

# list of pins to use (DO NOT CHANGE)
# board config according to schematics
#      9
# 2 5 8
# 1 4 7
# 0 3 6
pins = (
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5,
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9,
    board.GP10,
    board.GP18,
)

MEDIA = 1
KEY = 2
TYPE = 3
RUN = 4

keymap = {
    (0): (KEY, [Keycode.LEFT_CONTROL, Keycode.X]),
    (1): (TYPE, "Ramandeep Singh"),
    (2): (KEY, [Keycode.LEFT_CONTROL, Keycode.Z]),
    (3): (KEY, [Keycode.LEFT_CONTROL, Keycode.C]),
    (4): (TYPE, "ramandeep89@gmail.com"),
    (5): (KEY, [Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.Z]),
    (6): (KEY, [Keycode.LEFT_CONTROL, Keycode.V]),
    (7): (TYPE, "p3w.pew@yandex.com"),
    (8): (RUN, "wt.exe"),
    (9): (MEDIA, ConsumerControlCode.MUTE),
}

switches = []
for i in range(len(pins)):
    switch = DigitalInOut(pins[i])
    switch.direction = Direction.INPUT
    switch.pull = Pull.UP
    switches.append(switch)


switch_state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

encoder = rotaryio.IncrementalEncoder(board.GP16, board.GP17)
last_position = encoder.position

def keypress(key):
    if key[0] == KEY:
        kbd.send(*key[1])                        
    elif key[0] == MEDIA:
        cc.send(key[1])
    elif key[0] == TYPE:
        kbdl.write(key[1])
    elif key[0] == RUN:
        kbd.send(Keycode.GUI, Keycode.R)
        time.sleep(0.1)
        kbdl.write(key[1])
        time.sleep(0.1)
        kbd.send(Keycode.RETURN)
    else:
        print("unknown operation")

while True:
    
    current_position = encoder.position
    position_change = current_position - last_position
    if position_change > 0:
        for _ in range(position_change):
            cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        print(current_position)
    elif position_change < 0:
        for _ in range(-position_change):
            cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        print(current_position)
    last_position = current_position    
    
    for button in range(10):
        if not switch_state[button]:
            if not switches[button].value:
                try:
                    keypress(keymap[button])
                except ValueError:  # deals w six key limit
                    pass
                switch_state[button] = 1

        if switch_state[button]:
            if switches[button].value:
                switch_state[button] = 0

    time.sleep(0.01)  # debounce
    



