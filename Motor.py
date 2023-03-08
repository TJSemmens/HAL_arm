class Servo:

    MIN_PULSE = 0  # minimum pulse width in ms
    MAX_PULSE = 2
    ANGLE_CONST = 1  # measure the actual range of motion of the motor and get a number for total degrees spun / 180

    def __init__(self, pin, board, speed, min_angle=0, max_angle=180):
        board.set_pin_mode_servo(pin, self.MIN_PULSE, self.MAX_PULSE)
        self.board = board
        self.pin = pin
        self.angle = 0
        self.speed = speed
        self.min_angle = min_angle
        self.max_angle = max_angle

    def drive_to(self, angle):
        if self.min_angle <= angle <= self.max_angle:
            self.board.servo_write(self.pin, int(angle / self.ANGLE_CONST))
            self.angle = angle

    def drive(self, control_input=1):
        if self.min_angle < self.angle + self.speed * control_input < self.max_angle:
            self.angle += self.speed * control_input
        self.drive_to(self.angle)

    def drive_continuous(self, control_input):
        self.drive_to(90 + 90 * control_input)


    def zero(self):
        self.drive_to(90)


class Motor:
    MAX_ANALOG_OUT = 255

    def __init__(self, pwm_pin, logic_pins, board):
        board.set_pin_mode_pwm_output(pwm_pin)
        board.set_pin_mode_digital_output(logic_pins[0])
        board.set_pin_mode_digital_output(logic_pins[1])
        self.board = board
        self.pwm_pin = pwm_pin
        self.logic_pins = logic_pins
        self.direction = 0

    def drive(self, fraction_of_full_speed):
        if fraction_of_full_speed < 0 and self.direction == 0:
            self.board.digital_write(self.logic_pins[0], 1)
            self.board.digital_write(self.logic_pins[1], 0)
            self.direction = 1
        elif fraction_of_full_speed > 0 and self.direction == 1:
            self.board.digital_write(self.logic_pins[0], 0)
            self.board.digital_write(self.logic_pins[1], 1)
            self.direction = 0
        self.board.pwm_write(self.pwm_pin, int(abs(fraction_of_full_speed) * self.MAX_ANALOG_OUT))

    def zero(self):
        self.board.pwm_write(self.pwm_pin, 0)
        self.board.digital_write(self.logic_pins[0], 0)
        self.board.digital_write(self.logic_pins[1], 0)
        self.direction = 0


class CServo:
    def __init__(self, pin, board, speed):
        board.set_pin_mode_pwm_output(pin)
        self.board = board
        self.pin = pin
        self.speed = speed

    def drive(self, control_input):
        self.board.pwm_write(self.pin, int(control_input))

    def zero(self):
        self.board.pwm_write(self.pin, 0)
