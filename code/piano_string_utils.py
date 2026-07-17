import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import sounddevice as sd

def string_frequency(L, T, mu):
    '''L: length of string
    T: tension in string
    mu: linear mass density of string'''
    return (1 / (2*L)) * np.sqrt(T/mu)

def karplus_strong(f0, sample_rate, duration, seed=None):
    if seed is not None:
        np.random.seed(seed) # for reproducibility
    N = int(round(sample_rate / f0)) # Karplus-Strong requires an integer for N
    buffer = np.random.uniform(-1, 1, N)
    # Total number of samples to generate
    num_samples = int(sample_rate * duration) #  seconds^-1 * seconds 
    output = np.zeros(num_samples)

    for i in range(num_samples):
        # output current sample
        output[i] = buffer[0] # read oldest sample
        avg = 0.5 * (buffer[0] + buffer[1]) # average first two samples
        buffer = np.append(buffer[1:], avg) # shift buffer and add new sample
    
    return output, N

def get_fft(signal, sample_rate):
    '''Compute FFT, return positive-frequency freqs and magnitude.'''
    freqs = np.fft.fftfreq(len(signal), 1/sample_rate)
    mag = np.abs(np.fft.fft(signal))
    freqs_pos = freqs[freqs >= 0]
    mag_pos = mag[freqs >= 0]
    return freqs_pos, mag_pos

def find_signal_peaks(freqs_pos, mag_pos, height_frac=0.01, distance=20):
    '''Find peaks in a magnitude spectrum.'''
    peaks, properties = find_peaks(mag_pos, height=np.max(mag_pos) * height_frac, distance=distance)
    return freqs_pos[peaks]

def plot_fft(freqs_pos, mag_pos, title="FFT", xlim=(0, 10000)):
    plt.figure(figsize=(10, 6))
    plt.plot(freqs_pos, mag_pos)
    plt.xlim(xlim)
    plt.title(title)
    plt.ylabel("Magnitude")
    plt.xlabel("Frequency (Hz)")
    plt.show()

def check_peaks(signal, sample_rate, plot=True, title="FFT"):
    freqs_pos, mag_pos = get_fft(signal, sample_rate)
    peak_freqs = find_signal_peaks(freqs_pos, mag_pos)
    if plot:
        plot_fft(freqs_pos, mag_pos, title=title)
    return peak_freqs

def check_harmonics(signal, f0, sample_rate, num_harmonics = 5):
    '''Check if the peak frequency is a harmonic of f0.'''
    peak_freqs = check_peaks(signal, sample_rate, plot = False)
    peak_freq = peak_freqs[0]
    for n in range(1, num_harmonics + 1):
        target = n * f0
        expected = n * peak_freq
        actual = peak_freqs[n - 1]

        error_vs_expected = abs(expected - actual) / expected * 100
        error_vs_target = abs(target - actual) / target * 100

        print(f''' {'-'*10} Harmonic {n} {'-'*15} 
                        Expected (n * measured f0) ~{expected:.1f} Hz 
                        Target   (n * design f0)   ~{target:.1f} Hz 
                        Actual (FFT peak):          {actual:.1f} Hz 
                        % Error vs measured f0:     {error_vs_expected:.2f}%
                        % Error vs design target:   {error_vs_target:.2f}%
                        ''')
        

def plot_signal_shape(signal, sample_rate):
    freqs_pos, mag_pos = get_fft(signal, sample_rate)

    t = np.arange(len(signal)) / sample_rate
    n = int(0.01* sample_rate) # first 10 ms

    plt.figure(figsize=(10,3))
    plt.plot(t[:n], signal[:n])
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("Karplus-Strong Waveform, Signal AC (first 10 ms)")
    plt.show()


def test_sound(signal, sample_rate):
    sd.play(signal, sample_rate)
    sd.wait()

    t = np.arange(len(signal)) / sample_rate

def pure_tone(f0, sample_rate, duration):
    t = np.arange(int(sample_rate * duration)) / sample_rate
    return np.sin(2 * np.pi * f0 * t)

def freq_to_note(f, A4 = 440.0):
    '''Convert a frequency (Hz) to the nearest musical note name + octave,
    plus the deviation in cents (100 cents = 1 semitone) for tuning accuracy.'''
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Number of semitones from A4
    semitones_from_A4 = 12 * np.log2(f / A4)
    nearest_semitone = round(semitones_from_A4)
    
    # Deviation from the exact note, in cents (for reporting tuning accuracy)
    cents_off = (semitones_from_A4 - nearest_semitone) * 100
    
    # MIDI note number: A4 = MIDI note 69
    midi_number = 69 + nearest_semitone
    
    # Convert MIDI number to note name + octave
    note_index = midi_number % 12
    octave = (midi_number // 12) - 1  # MIDI octave numbering convention
    
    note_name = note_names[note_index]
    
    return f"{note_name}{octave}", cents_off