import time
from pymata4 import pymata4 as arduino
import XInput
from Motor import Servo, CServo

if __name__ == "__main__":
    # set up the electrical
    board = arduino.Pymata4()
    conveyor_l = Servo(13, board, 2)
    conveyor_r = Servo(12, board, 2)
    scissors = Servo(11, board, 1)
    wing_l = Servo(10, board, 1)
    wing_r = Servo(9, board, 1)
    all_motors = [conveyor_l, conveyor_r, scissors, wing_l, wing_r]

    # initialize the hardware
    for motor in all_motors:
        motor.zero()

    same_direction = False  # for conveyor belts
    print('starting input')
    while 1:
        # get state of all buttons on controller
        state = XInput.get_state(0)
        triggers = XInput.get_trigger_values(state)
        buttons = XInput.get_button_values(state)
        sticks = XInput.get_thumb_values(state)

        # set all motors based on controller values
        if not same_direction:
            conveyor_l.drive_continuous(triggers[0] - triggers[1])
            conveyor_r.drive_continuous(triggers[1] - triggers[0])
        elif same_direction:
            conveyor_l.drive_continuous(triggers[0] - triggers[1])
            conveyor_r.drive_continuous(triggers[0] - triggers[1])

        if buttons['X']:
            same_direction = False
        if buttons['Y']:
            same_direction = True

        if buttons['RIGHT_SHOULDER']:
            scissors.drive()
        elif buttons['LEFT_SHOULDER']:
            scissors.drive(-1)

        wing_r.drive(sticks[1][0])
        wing_l.drive(sticks[0][0])

        if buttons['A']:
            for motor in all_motors:
                motor.zero()


        time.sleep(0.01)
    print('all done')
