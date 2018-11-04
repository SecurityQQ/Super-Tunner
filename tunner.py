import numpy as np
import pygame
import pyaudio
import json
from time import sleep
from signals import Signal, Commands
from utils import *
from threading import Thread
from arrow import arrow

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.init()
sound_path = "/Users/aleksandrmalysev/Yandex.Disk.localized/Developer/PycharmProjects/organ/organ/notes/2/"

delay = 5
LAST_TIME_STAMP = arrow.datetime.now()

def play(path):
    global LAST_TIME_STAMP
    time_now = arrow.datetime.now()

    delta = time_now - LAST_TIME_STAMP

    if delta.total_seconds() < delay:
        return

    LAST_TIME_STAMP = time_now

    sound = pygame.mixer.Sound(path)
    sound.play()
    sleep(2)
    sound.fadeout(200)

COMMANDS = [
    {
      "label": "thank you",
      "triggers": lambda x: play(sound_path + "Ab.wav")
    },
    {
      "label": "toster sound",
      "triggers": lambda x: play(sound_path + "Bb.wav")
    }
  ]


class StreamProcesser:
    def __init__(self):
        self.states = ["INIT", "RUN_COMMANDS"]
        self.state = self.states[0]
        self.num_frames = 0
        self.added_cmd_idx = 0
        self.signal_capacity = 15
        self.signal = Signal(self.signal_capacity)
        self.commands = Commands()
        self.unlock_frame_num = 0

    def add_frame_freq(self, freq):
        self.num_frames += 1
        self.signal.push_note(freq)

        if self.num_frames <= FRAMES_PER_FFT:
            return

        if self.state == self.states[0]:
            self.add_freq_init(freq)
        else:
            self.add_freq_worker(freq)

    def add_freq_init(self, freq):
        if self.signal.is_correct() and self.unlock_frame_num < self.num_frames:
            add_cmd_result = self.commands.add_command(time_history=self.signal.history,
                                                  label=COMMANDS[self.added_cmd_idx]['label'],
                                                  triger_func=COMMANDS[self.added_cmd_idx]['triggers']
                                                )
            if add_cmd_result:
                self.unlock_frame_num = self.num_frames + self.signal_capacity + 1
                self.added_cmd_idx += 1

            if len(COMMANDS) == self.added_cmd_idx:
                self.state = self.states[-1]


    def add_freq_worker(self, freq):
        self.commands.trigger_command(self.signal.history,
                                 payload={"message": "signal_received: {}".format(self.signal.get_corrected_note())
                                          }
                                 )


def run_stream_processing():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
          dev = p.get_device_info_by_index(i)
          print((i,dev['name'],dev['maxInputChannels']))

    buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)

    window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))

    stream_proceser = StreamProcesser()

    def repeat_for_ages():
        stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                        channels=NUM_CHANNELS,
                                        rate=FSAMP,
                                        input_device_index=0,
                                        output_device_index=1,
                                        input=True,
                                        frames_per_buffer=FRAME_SIZE)
        stream.start_stream()
        while stream.is_active():
            # Shift the buffer down and new data in
            buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
            buf[-FRAME_SIZE:] = np.fromstring(stream.read(FRAME_SIZE), np.int16)

            # Run the FFT on the windowed buffer
            fft = np.fft.rfft(buf * window)

            # Get frequency of maximum response in range
            freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP

            # Get note number and nearest note

            stream_proceser.add_frame_freq(freq)

    while True:
        try:
            repeat_for_ages()
        except:
            pass


run_stream_processing()