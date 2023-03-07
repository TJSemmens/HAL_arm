import time
from pymata4 import pymata4 as arduino
import XInput
from Motor import Servo, CServo

SPEED = 2

if __name__ == "__main__":
    # set up the electrical
    board = arduino.Pymata4()
    conveyor_l = CServo(13, board)
    conveyor_r = CServo(12, board)
    scissors = Servo(11, board)
    wing_l = Servo(10, board)
    wing_r = Servo(9, board)
    all_motors = [conveyor_l, conveyor_r, scissors, wing_l, wing_r]

    # initialize the hardware
    for motor in all_motors:
        motor.zero()

    print('starting input')
    while 1:
        # get state of all buttons on controller
        state = XInput.get_state(0)
        triggers = XInput.get_trigger_values(state)
        buttons = XInput.get_button_values(state)
        sticks = XInput.get_thumb_values(state)

        # set all motors based on controller values
        conveyor_l.drive((triggers[0] - triggers[1]))
        conveyor_r.drive((triggers[1] - triggers[0]))

        if buttons['RIGHT_SHOULDER']:
            scissors.increment(SPEED)
        elif buttons['LEFT_SHOULDER']:
            scissors.increment(-SPEED)

        if buttons['DPAD_RIGHT']:
            wing_r.increment(-SPEED)
            wing_l.increment(SPEED)
        elif buttons['DPAD_LEFT']:
            wing_r.increment(SPEED)
            wing_l.increment(-SPEED)

        if buttons['A']:
            for motor in all_motors:
                motor.zero()

        time.sleep(0.001)
    print('all done')
