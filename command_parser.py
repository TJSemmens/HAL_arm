from word2number import w2n


class CommandParser:
    def __init__(self):
        self.motor = ''
        self.angle = 90

    def process_command(self, command):
        if 'left' in command:
            self.motor = 'left'
        if 'right' in command:
            self.motor = 'right'
        if 'both' in command:
            self.motor = 'both'
        if 'degrees' in command:
            try:
                self.angle =w2n.word_to_num(command)
            except ValueError:
                pass
