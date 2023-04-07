import command_parser as cmd
import time
from pymata4 import pymata4 as arduino
import XInput
import json
import Motor
import speech
from Motor import Servo
import deepspeech
import pyaudio
import numpy as np
import wavio

CONFIG_DATA = 'motor_configs'
RECORDED_PATH = 'recorded_path'

# speech related constants
RATE = 16000
CHUNK = int(RATE/20)
DURATION = 10
HOT_WORDS = 'left right roll pitch down in conveyor scissors wing wrist arm base lever five ten fifteen twenty'

if __name__ == "__main__":
    # initialize some variables
    same_direction = False  # for conveyor belts
    arm_controls = True  # for switching between wrist and arm controls
    voice_controls = False
    # load config file
    file = open(CONFIG_DATA)
    saved_configs = json.load(file)
    file.close()

    # set up the electrical
    board = arduino.Pymata4()
    conveyor_l = Servo('left conveyor', 13, board, 1)
    conveyor_r = Servo('right conveyor', 12, board, 1)
    scissors = Servo('scissors', 11, board, 1, zero_pos=saved_configs['11'])
    wing_l = Servo('left wing', 10, board, 1, zero_pos=saved_configs['10'])
    wing_r = Servo('right wing', 9, board, 1, zero_pos=saved_configs['9'])
    wrist_roll = Servo('wrist roll', 8, board, 0.2)
    wrist_pitch = Servo('wrist pitch', 7, board, 0.5, pulse_param=[0, 3])
    arm_base = Servo('arm base', 6, board, 0.5)
    arm_lever = Servo('arm lever', 5, board, 0.5, pulse_param=[0, 3])
    all_motors = [conveyor_l, conveyor_r, scissors, wing_l, wing_r, wrist_roll, wrist_pitch, arm_base, arm_lever]
    motor_dict = {'left conveyor': conveyor_l, 'right conveyor': conveyor_r, 'scissors': scissors, 'left wing': wing_l,
                  'right wing': wing_r, 'wrist roll': wrist_roll, 'wrist pitch': wrist_pitch, 'arm base': arm_base,
                  'arm lever': arm_lever}

    # initialize the hardware
    for motor in all_motors:
        motor.zero()

    # set up speech to text AI
    ds = deepspeech.Model('SpeechModel/deepspeech-0.9.3-models.pbmm')

    # start listening
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

    # Start an infinite loop for the control system
    print('starting input')
    while 1:
        # start an infinite loop for voice controls
        while voice_controls:
            # Interpret Speech
            audio = np.fromstring(stream.read(DURATION * RATE), dtype=np.int16)
            wavio.write("SpeechModel/wave.wav", audio, RATE, sampwidth=p.get_sample_size(format=pyaudio.paInt16))
            print('Running deepspeech')
            command = speech.run('SpeechModel/deepspeech-0.9.3-models.pbmm', "SpeechModel/wave.wav", HOT_WORDS,
                                 'SpeechModel/deepspeech-0.9.3-models.scorer')
            print(command)
            instr = cmd.CommandParser()
            instr.process_command(command)

            if instr.load_path:
                print('USING RECORDED PATH')
                file = open(RECORDED_PATH, 'r')
                path = json.load(file)
                instructions = Motor.parse_path(path)
                remaining = len(instructions['time'])
                step = 0
                while step < remaining:
                    motor_dict[instructions['name'][step]].drive_to(instructions['pos'][step])
                    step += 1
                    time.sleep(0.01)
                print('Path Completed')

            if instr.zero:
                for motor in all_motors:
                    motor.zero()

            if instr.angle and instr.motor:
                motor_dict[instr.motor].drive_to(motor_dict[instr.motor].angle + instr.angle)

            if instr.manual_controls:
                print('Exiting voice control.')
                voice_controls = False

        # get state of all buttons on controller
        state = XInput.get_state(0)
        triggers = XInput.get_trigger_values(state)
        buttons = XInput.get_button_values(state)
        sticks = XInput.get_thumb_values(state)

        # set all motors based on controller values
        if not same_direction:
            conveyor_l.drive_continuous(triggers[0] - triggers[1])
            conveyor_r.drive_continuous(triggers[1] - triggers[0])
        elif same_direction:
            conveyor_l.drive_continuous(triggers[0] - triggers[1])
            conveyor_r.drive_continuous(triggers[0] - triggers[1])

        if buttons['X']:
            same_direction = False
        if buttons['Y']:
            same_direction = True

        if buttons['RIGHT_SHOULDER']:
            scissors.drive()
        elif buttons['LEFT_SHOULDER']:
            scissors.drive(-1)

        if not arm_controls:
            wing_r.drive(sticks[1][0])
            wing_l.drive(sticks[0][0])

        if arm_controls:
            wrist_roll.drive_continuous(-sticks[1][0])
            wrist_pitch.drive(sticks[1][1])
            arm_base.drive_continuous(sticks[0][0])
            arm_lever.drive(-sticks[0][1])

        if buttons['A']:
            for motor in all_motors:
                motor.zero()

        if buttons['B']:
            save_data = dict()
            for motor in all_motors:
                motor.set_zero()
                save_data[str(motor.pin)] = motor.zero_pos
            file = open(CONFIG_DATA, 'w+')
            json.dump(save_data, file)
            file.close()
            print('New Zero Positions Saved.')

        if buttons['DPAD_LEFT']:
            all_path_data = {'name': [], 'time': [], 'pos': []}
            for motor in all_motors:
                motor.record = False
                index = 0
                for name in motor.path['name']:
                    all_path_data['name'].append(name)
                    all_path_data['time'].append(motor.path['time'][index])
                    all_path_data['pos'].append(motor.path['pos'][index])
                    index += 1
            file = open(RECORDED_PATH, 'w+')
            json.dump(all_path_data, file)
            file.close()
            print('Data Recorded.')

        if buttons['X']:
                for motor in all_motors:
                        print(f'motor: {motor.name}, angle: {motor.angle}')

        if buttons['DPAD_RIGHT']:
            for motor in all_motors:
                motor.record = True
                print('Beginning Recording.')

        if buttons['DPAD_DOWN']:
            print('USING RECORDED PATH')
            file = open(RECORDED_PATH, 'r')
            path = json.load(file)
            instructions = Motor.parse_path(path)
            remaining = len(instructions['time'])
            step = 0
            while step < remaining:
                motor_dict[instructions['name'][step]].drive_to(instructions['pos'][step])
                step += 1
                time.sleep(0.01)
            print('Path Completed')

        if buttons['RIGHT_THUMB']:
            arm_controls = True

        if buttons['LEFT_THUMB']:
            arm_controls = False

        if buttons['DPAD_UP']:
            print('Voice controls activated.')
            voice_controls = True

        time.sleep(0.01)

