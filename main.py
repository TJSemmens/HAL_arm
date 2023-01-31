import sys
import time
from pymata4 import pymata4 as arduino
import XInput
import Motor
import pyaudio
import numpy as np
import deepspeech
import wavio
import speech
import command_parser as cmd

RATE = 16000
CHUNK = int(RATE/20)
DURATION = 6
HOT_WORDS = 'left right motor degrees drive both'

if __name__ == "__main__":
    # set up the electrical
    board = arduino.Pymata4()
    motor_l = Motor.Motor(13, board)
    motor_r = Motor.Motor(12, board)

    # initialize the hardware
    motor_l.drive_to(90)
    motor_r.drive_to(90)


    # set up speech to text AI
    ds = deepspeech.Model('SpeechModel/deepspeech-0.9.3-models.pbmm')

    # start listening
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

    # Start an infinite loop for the control system
    print('starting controller input')
    start_time = time.time()
    while 1:
        # Interpret Speech
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
        state = XInput.get_state(0)
        triggers = XInput.get_trigger_values(state)
        motor_l.add_drive((triggers[0] - triggers[1]) * 2)
        motor_r.add_drive((triggers[1] - triggers[0]) * 2)
        time.sleep(0.005)
        '''
    print('all done')
