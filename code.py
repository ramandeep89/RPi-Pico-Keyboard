# RaspberryPi Pico Macroboard

import time
import asyncio
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

profile = 0

led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
async def blinkLED():
    while True:
        led.value = True
        await asyncio.sleep(0.05)
        led.value = False
        await asyncio.sleep(1/(profile+1))


led.value = profile

kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)
kbdl = KeyboardLayoutUS(kbd)

# list of pins to use (DO NOT CHANGE)

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

CHPRFL = -1 # (CHPRFL,) make sure to have comma before tuple end and each profile have atleast one CHPRFL keymap
SLEEP = 0 # (SLEEP, 1)
MEDIA = 1 # (MEDIA, ConsumerControlCode.MUTE)
KEY = 2 # (KEY, [Keycode.X]) OR (KEY, [Keycode.LEFT_CONTROL, Keycode.X])
TYPE = 3 # (TYPE, "Ramandeep Singh")
RUN = 4 # (RUN, "wt.exe")
MACRO = 5 # (MACRO, [(RUN, "wt.exe"), (SLEEP, 1), (TYPE, "ssh root@192.168.29.2")])

# board config keymap according to schematics
#      9
# 2 5 8
# 1 4 7
# 0 3 6
# board config encodermap according to schematics
# >> 0
# << 1

# keymap/encodermap is in format {(profile1): {(key1) : (MACRO),...}, ...}

keymap = {
    (0): {
        (0): (KEY, [Keycode.LEFT_CONTROL, Keycode.X]),
        (1): (TYPE, "Ramandeep Singh"),
        (2): (KEY, [Keycode.LEFT_CONTROL, Keycode.Z]),
        (3): (KEY, [Keycode.LEFT_CONTROL, Keycode.C]),
        (4): (TYPE, "ramandeep89@gmail.com"),
        (5): (KEY, [Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.Z]),
        (6): (KEY, [Keycode.LEFT_CONTROL, Keycode.V]),
        (7): (TYPE, "p3w.pew@yandex.com"),
        (8): (RUN, "wt.exe"),
        (9): (CHPRFL,),
    },
    (1): {
        (0): (KEY, [Keycode.LEFT_CONTROL, Keycode.X]),
        (1): (TYPE, "Ramandeep Singh"),
        (2): (KEY, [Keycode.LEFT_CONTROL, Keycode.Z]),
        (3): (KEY, [Keycode.LEFT_CONTROL, Keycode.C]),
        (4): (TYPE, "ramandeep89@gmail.com"),
        (5): (KEY, [Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.Z]),
        (6): (KEY, [Keycode.LEFT_CONTROL, Keycode.V]),
        (7): (TYPE, "p3w.pew@yandex.com"),
        (8): (MACRO, [(RUN, "wt.exe"), (SLEEP, 1), (TYPE, "ssh root@192.168.29.2")]),
        (9): (CHPRFL,),
    },
}

encoder = rotaryio.IncrementalEncoder(board.GP16, board.GP17)
encodermap = {
    (0): {
        (0): (MEDIA, ConsumerControlCode.VOLUME_INCREMENT),
        (1): (MEDIA, ConsumerControlCode.VOLUME_DECREMENT),
    },
    (1): {
        (0): (MEDIA, ConsumerControlCode.VOLUME_INCREMENT),
        (1): (MEDIA, ConsumerControlCode.VOLUME_DECREMENT),
    },
}

switches = []
for i in range(len(pins)):
    switch = DigitalInOut(pins[i])
    switch.direction = Direction.INPUT
    switch.pull = Pull.UP
    switches.append(switch)


switch_state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]



def keypress(key):
    global profile
    if key[0] == CHPRFL:
        profile = (profile+1) % len(keymap)
        led.value = profile % 2
    elif key[0] == SLEEP:
        time.sleep(key[1])
    elif key[0] == KEY:
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
    elif key[0] == MACRO:
        for macro in key[1]:
            keypress(macro)
    else:
        print("unknown operation")


async def main():
    last_position = encoder.position
    while True:
        current_position = encoder.position
        position_change = current_position - last_position
        if position_change > 0:
            for _ in range(position_change):
                keypress(encodermap[profile][0])
            print(current_position)
        elif position_change < 0:
            for _ in range(-position_change):
                keypress(encodermap[profile][1])
            print(current_position)
        last_position = current_position    
        
        for button in range(10):
            if not switch_state[button]:
                if not switches[button].value:
                    try:
                        keypress(keymap[profile][button])
                    except ValueError:  # deals w six key limit
                        pass
                    switch_state[button] = 1

            if switch_state[button]:
                if switches[button].value:
                    switch_state[button] = 0

        time.sleep(0.01)  # debounce
        

asyncio.run(main())
