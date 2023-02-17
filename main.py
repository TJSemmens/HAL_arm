import sys
import time
from pymata4 import pymata4 as arduino
import XInput
from Motor import Servo, CServo
import pyaudio
import numpy as np
import deepspeech
import wavio
import speech
import command_parser as cmd

SPEED = 2
RATE = 16000
CHUNK = int(RATE/20)
DURATION = 6
HOT_WORDS = 'left right motor degrees drive both'

if __name__ == "__main__":
    # set up the electrical
    board = arduino.Pymata4()
    conveyor_l = CServo(13, board)
    conveyor_r = CServo(12, board)
    scissors = Servo(11, board)
    wing_l = Servo(10, board)
    wing_r = Servo(9, board)
    all_motors = [conveyor_l, conveyor_r, scissors, wing_l, wing_r]

    # initialize the hardware
    for motor in all_motors:
        motor.zero()

    # set up speech to text AI
    # ds = deepspeech.Model('SpeechModel/deepspeech-0.9.3-models.pbmm')

    # start listening
    # p = pyaudio.PyAudio()
    # stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

    # Start an infinite loop for the control system
    print('starting input')
    while 1:
        # Interpret Speech
        '''
        audio = np.fromstring(stream.read(DURATION * RATE), dtype=np.int16)
        wavio.write("SpeechModel/wave.wav", audio, RATE, sampwidth=p.get_sample_size(format=pyaudio.paInt16))
        print('running deepspeech')
        command = speech.run('SpeechModel/deepspeech-0.9.3-models.pbmm', "SpeechModel/wave.wav", HOT_WORDS,
                             'SpeechModel/deepspeech-0.9.3-models.scorer')
        print(command)
        instr = cmd.CommandParser()
        instr.process_command(command)
        print(instr.angle)
        if instr.motor == 'left':
            motor_l.drive_to(instr.angle)
        elif instr.motor == 'right':
            motor_r.drive_to(instr.angle)
        elif instr.motor == 'both':
            motor_r.drive_to(instr.angle)
            motor_l.drive_to(instr.angle)
        else:
            pass
        '''

        # get state of all buttons on controller
        state = XInput.get_state(0)
        triggers = XInput.get_trigger_values(state)
        buttons = XInput.get_button_values(state)
        sticks = XInput.get_thumb_values(state)

        # set all motors based on controller values
        conveyor_l.drive((triggers[0] - triggers[1]))
        conveyor_r.drive((triggers[1] - triggers[0]))

        if buttons['RIGHT_SHOULDER']:
            scissors.increment(SPEED)
        elif buttons['LEFT_SHOULDER']:
            scissors.increment(-SPEED)

        if buttons['DPAD_RIGHT']:
            wing_r.increment(-SPEED)
            wing_l.increment(SPEED)
        elif buttons['DPAD_LEFT']:
            wing_r.increment(SPEED)
            wing_l.increment(-SPEED)

        if buttons['A']:
            for motor in all_motors:
                motor.zero()

        time.sleep(0.001)
    print('all done')
