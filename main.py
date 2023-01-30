import time

from pymata4 import pymata4 as arduino

if __name__ == "__main__":
    board = arduino.Pymata4()
    board.set_pin_mode_servo(13, 1, 2)
    board.servo_write(13, 0)
    time.sleep(1)

    board.servo_write(13, 90)
    time.sleep(1)

    board.servo_write(13, 180)
    time.sleep(1)

    print('all done')
