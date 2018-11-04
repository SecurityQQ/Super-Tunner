import numpy as np

NOTE_MIN = 60  # C4
NOTE_MAX = 69  # A4
FSAMP = 22050  # Sampling frequency in Hz
NUM_CHANNELS = 1
FRAME_SIZE = 2048 * NUM_CHANNELS  # How many samples per frame?
FRAMES_PER_FFT = 16  # FFT takes average across how many frames?

SAMPLES_PER_FFT = FRAME_SIZE * FRAMES_PER_FFT
FREQ_STEP = float(FSAMP) / SAMPLES_PER_FFT

NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()


def number_to_freq(n): return 440 * 2.0 ** ((n - 69) / 12.0)
def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
def note_name(n): return NOTE_NAMES[n % 12] + str(n // 12 - 1)
def note_to_fftbin(n): return number_to_freq(n) / FREQ_STEP


imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN - 1))))
imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX + 1))))
