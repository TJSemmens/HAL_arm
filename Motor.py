import math
import time
import pandas as pd

class Servo:

    MIN_PULSE = 0  # minimum pulse width in ms
    MAX_PULSE = 2
    ANGLE_CONST = 1  # measure the actual range of motion of the motor and get a number for total degrees spun / 180
    ACC_CURVE = [0]
    i = 1
    while i < 100:
        ACC_CURVE.append(1/(1+math.exp(-7*(i-0.7))))
        i += 1

    def __init__(self, name, pin, board, speed, min_angle=0, max_angle=180, zero_pos=90):
        board.set_pin_mode_servo(pin, self.MIN_PULSE, self.MAX_PULSE)
        self.board = board
        self.pin = pin
        self.name = name
        self.angle = 0
        self.speed = speed
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.acc_curve_pos = 0
        self.zero_pos = zero_pos
        self.record = False
        self.path = {'name': [], 'time': [], 'pos': []}

    def drive_to(self, angle):
        if self.min_angle <= angle <= self.max_angle:
            self.board.servo_write(self.pin, int(angle / self.ANGLE_CONST))
            self.angle = angle
            current_time = time.time()
            if self.record:
                self.path['name'].append(self.name)
                self.path['time'].append(current_time)
                self.path['pos'].append(angle)

    def drive(self, control_input=1):
        if control_input == 0:
            self.acc_curve_pos = 0
        elif self.acc_curve_pos < 99:
            self.acc_curve_pos += 1
        if self.min_angle < self.angle + self.speed * control_input < self.max_angle:
            self.angle += self.speed * control_input * self.ACC_CURVE[self.acc_curve_pos]
        self.drive_to(self.angle)

    def drive_continuous(self, control_input):
        self.drive_to(90 + 90 * control_input)

    def zero(self):
        self.drive_to(self.zero_pos)

    def set_zero(self):
        self.zero_pos = self.angle
        return self.zero_pos


def parse_path(path_data):
    df = pd.DataFrame(path_data)
    df.set_index('time')
    df.sort_index(ascending=True)
    df = df.to_dict()
    return df
