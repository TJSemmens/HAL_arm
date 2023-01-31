class Motor:

    MIN_PULSE = 0  # minimum pulse width in ms
    MAX_PULSE = 2
    ANGLE_CONST = 1  # measure the actual range of motion of the motor and get a number for total degrees spun / 180

    def __init__(self, pin, board):
        board.set_pin_mode_servo(pin, self.MIN_PULSE, self.MAX_PULSE)
        self.board = board
        self.pin = pin
        self.angle = 0

    def drive_to(self, angle):
        if 0 <= angle <= 180:
            self.board.servo_write(self.pin, int(angle / self.ANGLE_CONST))
            self.angle = angle

    def add_drive(self, amount):
        if 0 < self.angle + amount < 180:
            self.angle += amount
        self.drive_to(self.angle)
