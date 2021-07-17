# Default values


SAMPLE_RATE = 22050
# When a file is fingerprinted it is resampled to SAMPLE_RATE Hz.


PEAK_BOX_SIZE = 30

# The number of points in a spectrogram around a peak for it to be considered a peak.


POINT_EFFICIENCY = 0.8
# A factor between 0 and 1 that determines the number of peaks found for each file.


TARGET_START = 0.05
# How many seconds after an anchor point to start the target zone for pairing.


TARGET_T = 1.8
# The width of the target zone in seconds.


TARGET_F = 4000
""" The height of the target zone in Hz. Higher means higher accuracy.
Can range from 0 - (0.5 * SAMPLE_RATE).
"""

FFT_WINDOW_SIZE = 0.1
""" The number of seconds of audio to use in each spectrogram segment. Larger windows mean higher
frequency resolution but lower time resolution in the spectrogram.
"""

DB_PATH = r"C:\Users\AMRITA\PycharmProjects\pythonProject4\detecttunes\hash.db"
""" Path to the database file to use. """

NUM_WORKERS = 8
""" Number of workers to use when registering songs. """
