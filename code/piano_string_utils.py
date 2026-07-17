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
