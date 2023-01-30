class Motor:

    MIN_PULSE = 0  # minimum pulse width in ms
    MAX_PULSE = 2
    ANGLE_CONST = 1  # measure the actual range of motion of the motor and get a number for total degrees spun / 180

    def __init__(self, pin, board):
        board.set_pin_mode_servo(pin, self.MIN_PULSE, self.MAX_PULSE)
        self.board = board
        self.pin = pin

    def drive_to(self, angle):
        self.board.servo_write(self.pin, int(angle / self.ANGLE_CONST))
