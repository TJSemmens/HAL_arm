import time
from pymata4 import pymata4 as arduino
import XInput
import json
from Motor import Servo, CServo

CONFIG_DATA = 'motor_configs'

if __name__ == "__main__":
    # load config file
    file = open(CONFIG_DATA)
    saved_configs = json.load(file)
    file.close()
    # set up the electrical
    board = arduino.Pymata4()
    conveyor_l = Servo(13, board, 2)
    conveyor_r = Servo(12, board, 2)
    scissors = Servo(11, board, 1, min_angle=86, max_angle=136, zero_pos=saved_configs['11'])
    wing_l = Servo(10, board, 2, min_angle=64, max_angle=180, zero_pos=saved_configs['10'])
    wing_r = Servo(9, board, 2, min_angle=59, max_angle=180, zero_pos=saved_configs['9'])
    wrist_roll = Servo(8, board, 2)
    wrist_pitch = Servo(7, board, 2)
    arm_base = Servo(6, board, 2)
    all_motors = [conveyor_l, conveyor_r, scissors, wing_l, wing_r, wrist_roll, wrist_pitch, arm_base]


    # initialize the hardware
    for motor in all_motors:
        motor.zero()

    same_direction = False  # for conveyor belts
    arm_controls = True # for switching between wrist and arm controls
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

        if not arm_controls:
            wing_r.drive(sticks[1][0])
            wing_l.drive(sticks[0][0])

        if arm_controls:
            wrist_roll.drive_continuous(sticks[1][0])
            wrist_pitch.drive(sticks[1][1])
            arm_base.drive_continuous(sticks[0][0])

        if buttons['A']:
            for motor in all_motors:
                motor.zero()

        if buttons['B']:
            save_data = dict()
            for motor in all_motors:
                motor.set_zero()
                save_data[str(motor.pin)] = motor.zero_pos
            file = open(CONFIG_DATA, 'w+')
            json.dump(save_data, file)
            file.close()

        if buttons['DPAD_LEFT']:
            for motor in all_motors:
                print(motor.angle)

        if buttons['DPAD_DOWN']:
            arm_controls = True

        if buttons['DPAD_UP']:
            arm_controls = False


        time.sleep(0.01)
    print('all done')
