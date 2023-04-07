from word2number import w2n


class CommandParser:
    def __init__(self, motor_dict):
        self.motor_dict = motor_dict
        self.load_path = False
        self.manual_controls = False
        self.motor = None
        self.angle = None
        self.zero = False

    def process_command(self, command):
        # function variables
        negative_keywords = ['down', 'in', 'left']

        # find the angle in the command
        try:
            self.angle = w2n.word_to_num(command)
        except ValueError:
            pass

        # find the desired motor
        for key in self.motor_dict.keys():
            if key in command:
                self.motor = key

        # flip the angle based on keywords
        for word in negative_keywords:
            if word in command:
                self.angle *= -1

        # check for global commands
        if 'zero' in command:
            self.zero = True

        if 'load' in command or 'path' in command:
            self.load_path = True

        if 'manual' in command:
            self.manual_controls = True
