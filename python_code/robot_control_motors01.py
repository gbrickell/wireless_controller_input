#!/usr/bin/env python3
"""
based upon:
robot_control_inputs.py
www.bluetin.io
 and further developed by Enmore Green Ltd
command:  python3 /home/pi/wireless_controller_input/robot_control_motors01.py
"""

import sys
from inputs import get_gamepad
from inputs import devices
for device in devices:
    print(device)

################################
# GPIO set up
################################
import RPi.GPIO as GPIO # Import the GPIO Library - still using this for PWM
# Set the GPIO modes using GPIO 
GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False) 


###########################################################################################
# Dictionary of the 19 game controller buttons/joysticks on the PiHut witeless controller
# which is recognised by the 'inputs' module as a "MS X-Box 360 pad"
###########################################################################################
controller_input = {'BTN_THUMBL': 0, 'ABS_X': 0, 'ABS_Y': 0, 'BTN_THUMBR': 0,  'ABS_RX': 0, 'ABS_RY': 0, 
                    'BTN_START': 0, 'BTN_SELECT': 0, 'BTN_MODE': 0,  'ABS_HAT0X': 0, 'ABS_HAT0Y': 0, 
                    'BTN_WEST': 0, 'BTN_NORTH': 0, 'BTN_SOUTH': 0, 'BTN_EAST': 0,
                    'BTN_TL': 0, 'BTN_TR': 0, 'ABS_Z': 0, 'ABS_RZ': 0 }

################################
# drive motor set ups
################################
# L298N setup code
# Define Outputs from RPi to L298N - variable names are as per the L298N pin labels
# these GPIO pins are in the 'defaults' file but are hard coded here
enA = 15   # this will be a software set PWM pin
in1 = 8
in2 = 11
enB = 18   # this will be a software set PWM pin
in3 = 9
in4 = 10

motorspeed = 100

# set the various PWM parameters
# How many times to turn the GPIO pin on and off each second 
Frequency = 20   # usually 20
# How long the GPIO pin stays on each cycle, as a percent  
# Setting the duty cycle to 0 means the motors will not turn
DutyCycleA = 60      # usually 60
DutyCycleB = 60      # usually 60

# Set the GPIO Pin mode - all set as OUTPUTs
GPIO.setup(enA, GPIO.OUT)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(enB, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)

pwm_enA = GPIO.PWM(enA, Frequency)  # set the enA pin as a software set PWM pin
pwm_enB = GPIO.PWM(enB, Frequency)  # set the enB pin as a software set PWM pin
# Start the software PWM pins with a duty cycle of 0 (i.e. motors not moving)
pwm_enA.start(0)
pwm_enB.start(0)



##################################################
##        joystick axes mixer function          ##
##    for use with the PiHut controller         ##
##    and using the Python 'inputs' module      ##
##################################################
def mixer(yaw, throttle, max_power=100):   # max_power set to 100 for L298N use
    """
    Mix a pair of joystick axes, returning a pair of wheel power settings. This is where the mapping from
    joystick positions to wheel powers is defined, so any changes to how the robot drives should be made here
    
    :param yaw: 
        Yaw axis values normalised to the range from -1.0 to 1.0 before it gets here
    :param throttle: 
        Throttle axis value normalised to the range from -1.0 to 1.0 before it gets here
    :param max_power: 
        Maximum speed that should be returned from the mixer, defaults to 100
    :return: 
        A pair of power_left, power_right integer duty cycle values to send to the motor driver
    """
    left = throttle + yaw
    right = throttle - yaw
    scale = float(max_power) / max(1, abs(left), abs(right))
    return int(left * scale), int(right * scale)



##########################################################################
# L298N motor control - function for wireless control this allows the 
#   motor(s) on each of the robot to be set separately
##########################################################################
def motor_pwm(leftright, dutycycle):  # 
    global debug
    global OLED_update
    global RGB_update

    dutycycle = int(dutycycle) # force as an integer just in case
    # individual motor control with a +'ve or -'ve dutycycle to set the motor forwards or backwards
    if leftright == "left":  # left motor is motor A
        if dutycycle == 0:   # stop the motor
            # motor braking
            # set enA with 100% PWM dutycycle
            pwm_enA.start(100)
            # set in1 off and in2 off i.e. LOW- LOW for no motion
            GPIO.output(in1, 0)
            GPIO.output(in2, 0)
        elif dutycycle > 0:  # move forwards
            # set enA with the PWM dutycycle
            pwm_enA.start(dutycycle)
            # set in1 on and in2 off i.e. HIGH - LOW for forward motion
            GPIO.output(in1, 1)
            GPIO.output(in2, 0)
        elif dutycycle < 0:  # move backwards
            # set enA with the PWM dutycycle
            pwm_enA.start(abs(dutycycle))
            # set in1 on and in2 off i.e. HIGH - LOW for forward motion
            GPIO.output(in1, 0)
            GPIO.output(in2, 1)

    elif leftright == "right":  # right motor is motor B
        if dutycycle == 0:   # stop the moter
            # motor braking
            # set enB with 100% PWM dutycycle
            pwm_enB.start(100)
            # set in1 off and in2 off i.e. LOW- LOW for no motion
            GPIO.output(in3, 0)
            GPIO.output(in4, 0)
        elif dutycycle > 0:  # move forwards
            # set enB with the PWM dutycycle
            pwm_enB.start(dutycycle)
            # set in3 off and in4 on - reversed for LOW - HIGH so that both motors go fwd
            GPIO.output(in3, 0)
            GPIO.output(in4, 1)
        elif dutycycle < 0:  # move backwards
            # set enB with the PWM dutycycle
            pwm_enB.start(abs(dutycycle))
            # set in3 on and in4 off - reversed for HIGH - LOW so that both motors go back
            GPIO.output(in3, 1)
            GPIO.output(in4, 0)

    else: #wrong motor type set
        print ("motor_pwm function: wrong motor type set")
        print (" ")



#-----------------------------------------------------------

def gamepad_update():
    # Code execution stops at the following line until gamepad event occurs.
    events = get_gamepad()
    print ("gamepad_update: events")
    print (events)
    return_code = 'No Match'
    #print (" length of events: " + str(len(events)) )
    for event in events:
        print ("gamepad_update: event.code")
        print (event.code)
        print ("gamepad_update: event.state")
        print (event.state)
        event_test = controller_input.get(event.code, 'No Match')
        if event_test != 'No Match':
            controller_input[event.code] = event.state
            return_code = event.code
        else:
            return_code = 'No Match'

    return return_code

#-----------------------------------------------------------

def drive_controlxy_left():        # function to simulate driving robot motors using the left hand joystick
    # Get joystick values from the left analogue stick
    x_axis = controller_input['ABS_X']/32768
    y_axis = -(controller_input['ABS_Y'] + 1)/32768  # change the sign as forward movements give negative values
                                                     #  and add 1 as it doesn't seem to zero
    # Get power from mixer function
    power_right, power_left = mixer(yaw=x_axis, throttle=y_axis)  # need to reverse left/right for some reason???
    print ("left-right power outputs: " + str(power_left) + " - " + str(power_right) )


    # x-axis output
    print('x-axis output --> {}' .format(x_axis) )
    # y-axis output: with tewaks!
    print('y-axis output --> {}' .format(y_axis) )

#-----------------------------------------------------------
def drive_motors():
    # Get joystick values from the left analogue stick
    x_axis = controller_input['ABS_X']/32768
    y_axis = -(controller_input['ABS_Y'] + 1)/32768  # change the sign as forward movements give negative values
                                                     #  and add 1 as it doesn't seem to zero
    # Get power from mixer function
    power_right, power_left = mixer(yaw=x_axis, throttle=y_axis)  # need to reverse left/right for some reason???

    # x-axis output
    print('x-axis output --> {}' .format(x_axis) )
    # y-axis output: with tewaks!
    print('y-axis output --> {}' .format(y_axis) )

    # Set the left and right motors' forward/backwards speeds according to the power settings above
    motor_pwm("left", power_left)
    motor_pwm("right", power_right)
    print ("motor power settings: " + str(power_left) + " - " + str(power_right) )

#-----------------------------------------------------------
def drive_controlxy_right():
    # function to drive robot motors using the right hand joystick
    # x-axis output
    print('x-axis output --> {}' .format(controller_input['ABS_RX']) )
    # y-axis output
    print('y-axis output --> {}' .format(controller_input['ABS_RY']) )

#-----------------------------------------------------------

def abs_z():
    # Function to do something when the rear/bottom (2) left-hand (ABS_Z) btn is held down for a period of time
    print('ABS_Z button movement --> {}' .format(controller_input['ABS_Z']) )

#-----------------------------------------------------------

def abs_rz():
    # Function to do something when the rear/bottom (2) right-hand (ABS_RZ) btn is held down for a period of time
    print('ABS_RZ button movement --> {}' .format(controller_input['ABS_RZ']) )

#-----------------------------------------------------------

def abs_hat0x():
    # Function to do something when either of the x-axis pads (ABS_HAT0X) are pressed
    print('ABS_HAT0X pad pressed --> {}' .format(controller_input['ABS_HAT0X']) )

#-----------------------------------------------------------

def abs_hat0y():
    # Function to do something when either of the y-axis pads (ABS_HAT0Y) are pressed
    print('ABS_HAT0Y pad pressed --> {}' .format(controller_input['ABS_HAT0Y']) )

#-----------------------------------------------------------

def btn_thumbl():
    # Function to do something when BTN_THUMBL is pressed
    print('BTN_THUMBL pressed --> {}' .format(controller_input['BTN_THUMBL']) )

#-----------------------------------------------------------

def btn_thumbr():
    # Function to do something when BTN_THUMBR is pressed
    print('BTN_THUMBR pressed --> {}' .format(controller_input['BTN_THUMBR']) )

#-----------------------------------------------------------

def btn_start():
    # Function to do something when BTN_START is pressed
    print('BTN_START pressed --> {}' .format(controller_input['BTN_START']) )

#-----------------------------------------------------------

def btn_select():
    # Function to do something when BTN_SELECT is pressed
    print('BTN_SELECT pressed --> {}' .format(controller_input['BTN_SELECT']) )

#-----------------------------------------------------------

def btn_mode():
    # Function to do something when BTN_MODE is pressed
    print('BTN_MODE pressed --> {}' .format(controller_input['BTN_MODE']) )

#-----------------------------------------------------------

def btn_north():
    # Function to do something when BTN_NORTH is pressed
    print('BTN_NORTH pressed --> {}' .format(controller_input['BTN_NORTH']) )

#-----------------------------------------------------------

def btn_east():
    # Function to do something when BTN_EAST is pressed
    print('BTN_EAST pressed --> {}' .format(controller_input['BTN_EAST']) )

#-----------------------------------------------------------

def btn_south():
    # Function to do something when BTN_SOUTH is pressed
    print('BTN_SOUTH pressed --> {}' .format(controller_input['BTN_SOUTH']) )

#-----------------------------------------------------------

def btn_west():
    # Function to do something when BTN_WEST is pressed
    print('BTN_WEST pressed --> {}' .format(controller_input['BTN_WEST']) )

#-----------------------------------------------------------

def btn_tl():
    # Function to do something when BTN_TL is pressed
    print('BTN_TL pressed --> {}' .format(controller_input['BTN_TL']) )

#-----------------------------------------------------------

def btn_tr():
    # Function to do something when BTN_TR is pressed
    print('BTN_TR pressed --> {}' .format(controller_input['BTN_TR']) )

#-----------------------------------------------------------


def main():
    """ Main entry point of the app """
    while 1:
        # Get next controller Input
        sys.stdin.flush()
        control_code = gamepad_update()
        
        # Gamepad button/joystick filter
        if control_code == 'ABS_X' or control_code == 'ABS_Y':
            # Drive and steering using left joystick
            #drive_controlxy_left() # this just prints out the x and y values 
            drive_motors()
        elif control_code == 'ABS_RX' or control_code == 'ABS_RY':
            # Drive and steering right joystick
            drive_controlxy_right()
        elif control_code == 'ABS_Z':
            # rear/left btn held down
            abs_z()
        elif control_code == 'ABS_RZ':
            # rear/right btn held down
            abs_rz()
        elif control_code == 'ABS_HAT0X':
            # joypad pressed
            abs_hat0x()
        elif control_code == 'ABS_HAT0Y':
            # joypad pressed
            abs_hat0y()
        elif control_code == 'BTN_SOUTH':
            # btn pressed
            btn_south()
        elif control_code == 'BTN_WEST':
            # btn pressed
            btn_west()
        elif control_code == 'BTN_NORTH':
            # btn pressed
            btn_north()
        elif control_code == 'BTN_EAST':
            # btn pressed
            btn_east()
        elif control_code == 'BTN_START':
            # btn pressed
            btn_start()
        elif control_code == 'BTN_SELECT':
            # btn pressed
            btn_select()
        elif control_code == 'BTN_MODE':
            # btn pressed
            btn_mode()
        elif control_code == 'BTN_THUMBR':
            # btn pressed
            btn_thumbr()
        elif control_code == 'BTN_THUMBL':
            # btn pressed
            btn_thumbl()
        elif control_code == 'BTN_TL':
            # btn pressed
            btn_tl()
        elif control_code == 'BTN_TR':
            # btn pressed
            btn_tr()
        #else:
        #    print (str(control_code) + " control not recognised")

#-----------------------------------------------------------

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()