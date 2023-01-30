import time
from pyPS4Controller.controller import Controller
from pymata4 import pymata4 as arduino

import Motor

if __name__ == "__main__":
    board = arduino.Pymata4()
    ctrl = Controller()
    motor = Motor.Motor(13, board)


    print('all done')
