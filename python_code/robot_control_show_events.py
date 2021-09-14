#!/usr/bin/env python3

#  from the python inputs module documentation

# command - python3 /home/pi/wireless_controller_input/robot_control_show_events.py

from inputs import get_gamepad
from inputs import devices
for device in devices:
    print(device)

while 1:
    events = get_gamepad()
    for event in events:
        print(event.ev_type, event.code, event.state)

