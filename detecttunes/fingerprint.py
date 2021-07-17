import uuid
import numpy as np
from detecttunes.settings import (
    SAMPLE_RATE, FFT_WINDOW_SIZE, POINT_EFFICIENCY, PEAK_BOX_SIZE,
    TARGET_START, TARGET_T, TARGET_F
)
from pydub import AudioSegment
from scipy.signal import spectrogram
from scipy.ndimage import maximum_filter


def my_spectrogram(audio):
    """Helper function that performs a spectrogram with the values in settings."""
    nperseg = int(SAMPLE_RATE * FFT_WINDOW_SIZE)
    return spectrogram(audio, SAMPLE_RATE, nperseg=nperseg)


def file_to_spectrogram(filename):
    """Calculates the spectrogram of a file.

    Converts a file to mono and resamples to :data:`~detecttunes.settings.SAMPLE_RATE` before
    calculating. Uses :data:`~detecttunes.settings.FFT_WINDOW_SIZE` for the window size.

    :param filename: Path to the file to spectrogram.
    :returns: * f - list of frequencies
              * t - list of times
              * Sxx - Power value for each time/frequency pair
    """
    a = AudioSegment.from_file(filename).set_channels(1).set_frame_rate(SAMPLE_RATE)
    audio = np.frombuffer(a.raw_data, np.int16)
    return my_spectrogram(audio)


def find_peaks(sxx):
    """Finds peaks in a spectrogram.

    Uses :data:`~detecttunes.settings.PEAK_BOX_SIZE` as the size of the region around each
    peak. Calculates number of peaks to return based on how many peaks could theoretically
    fit in the spectrogram and the :data:`~detecttunes.settings.POINT_EFFICIENCY`.

    Inspired by
    `photutils
    <https://photutils.readthedocs.io/en/stable/_modules/photutils/detection/core.html#find_peaks>`_.

    :param sxx: The spectrogram.
    :returns: A list of peaks in the spectrogram.
    """
    data_max = maximum_filter(sxx, size=PEAK_BOX_SIZE, mode='constant', cval=0.0)
    peak_good_mask = (sxx == data_max)  # good pixels are True
    y_peaks, x_peaks = peak_good_mask.nonzero()
    peak_values = sxx[y_peaks, x_peaks]
    i = peak_values.argsort()[::-1]
    # get co-ordinates into arr
    j = [(y_peaks[idx], x_peaks[idx]) for idx in i]
    total = sxx.shape[0] * sxx.shape[1]
    # in a square with a perfectly spaced grid, we could fit area / PEAK_BOX_SIZE^2 points
    # use point efficiency to reduce this, since it won't be perfectly spaced
    # accuracy vs speed tradeoff
    peak_target = int((total / (PEAK_BOX_SIZE**2)) * POINT_EFFICIENCY)
    return j[:peak_target]


def idxs_to_tf_pairs(idxs, t, f):
    """Helper function to convert time/frequency indices into values."""
    return np.array([(f[i[0]], t[i[1]]) for i in idxs])


def hash_point_pair(p1, p2):
    """Helper function to generate a hash from two time/frequency points."""
    return hash((p1[0], p2[0], p2[1]-p2[1]))


def target_zone(anchor, points, width, height, t):
    """Generates a target zone as described in `the Shazam paper
    <https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf>`_.

    Given an anchor point, yields all points within a box that starts `t` seconds after the point,
    and has width `width` and height `height`.

    :param anchor: The anchor point
    :param points: The list of points to search
    :param width: The width of the target zone
    :param height: The height of the target zone
    :param t: How many seconds after the anchor point the target zone should start
    :returns: Yields all points within the target zone.
    """
    x_min = anchor[1] + t
    x_max = x_min + width
    y_min = anchor[0] - (height*0.5)
    y_max = y_min + height
    for point in points:
        if point[0] < y_min or point[0] > y_max:
            continue
        if point[1] < x_min or point[1] > x_max:
            continue
        yield point


def hash_points(points, filename):
    """Generates all hashes for a list of peaks.

    Iterates through the peaks, generating a hash for each peak within that peak's target zone.

    :param points: The list of peaks.
    :param filename: The filename of the song, used for generating song_id.
    :returns: A list of tuples of the form (hash, time offset, song_id).
    """
    hashes = []
    song_id = uuid.uuid5(uuid.NAMESPACE_OID, filename).int
    for anchor in points:
        for target in target_zone(
            anchor, points, TARGET_T, TARGET_F, TARGET_START
        ):
            hashes.append((
                # hash
                hash_point_pair(anchor, target),
                # time offset
                anchor[1],
                # filename
                str(song_id)
            ))
    return hashes


def fingerprint_file(filename):
    """Generate hashes for a file.

    Given a file, runs it through the fingerprint process to produce a list of hashes from it.

    :param filename: The path to the file.
    :returns: The output of :func:`hash_points`.
    """
    f, t, sxx = file_to_spectrogram(filename)
    peaks = find_peaks(sxx)
    peaks = idxs_to_tf_pairs(peaks, t, f)
    return hash_points(peaks, filename)


def fingerprint_audio(frames):
    """Generate hashes for a series of audio frames.

    Used when recording audio.

    :param frames: A mono audio stream. Data type is any that ``scipy.signal.spectrogram`` accepts.
    :returns: The output of :func:`hash_points`.
    """
    f, t, sxx = my_spectrogram(frames)
    peaks = find_peaks(sxx)
    peaks = idxs_to_tf_pairs(peaks, t, f)
    return hash_points(peaks, "recorded")
