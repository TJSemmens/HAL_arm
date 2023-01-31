import sys
import time
from pymata4 import pymata4 as arduino
import XInput
import Motor
import pyaudio
import numpy as np
import deepspeech

RATE = 44100
CHUNK = int(RATE/20)

if __name__ == "__main__":
    # set up the electrical
    board = arduino.Pymata4()
    motor_l = Motor.Motor(13, board)
    motor_r = Motor.Motor(12, board)

    # initialize the hardware
    motor_l.drive_to(90)
    motor_r.drive_to(90)
    print('starting controller input')

    # set up speech to text AI
    ds = deepspeech.Model('SpeechModel/deepspeech-0.9.3-models.pbmm')

    # start listening
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

    # Start an infinite loop for the control system
    while 1:
        audio = np.fromstring(stream.read(CHUNK), dtype=np.int16)
        state = XInput.get_state(0)
        triggers = XInput.get_trigger_values(state)
        motor_l.add_drive((triggers[0] - triggers[1]) * 2)
        motor_r.add_drive((triggers[1] - triggers[0]) * 2)
        time.sleep(0.005)

    print('all done')
