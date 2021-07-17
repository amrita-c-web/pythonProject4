import os
import numpy as np
from multiprocessing import Pool
from tinytag import TinyTag
from detecttunes.fingerprint import fingerprint_file
from detecttunes.settings import NUM_WORKERS
from detecttunes.storage import store_song, get_matches, get_info_for_song_id, song_in_db

KNOWN_EXTENSIONS = ["mp3", "wav"]


def get_song_info(filename):
    tag = TinyTag.get(filename)
    return tag.albumartist, tag.album, tag.title


def register_song(filename):
    """
    Checks if the song is already registered based on path provided and ignores
    those that are already registered.

"""
    if song_in_db(filename):
        return
    else:
        hashes = fingerprint_file(filename)
        song_info = get_song_info(filename)
        store_song(hashes, song_info)


def register_directory(path):
    """  register songs in a directory.
    """
    to_register = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.split('.')[-1] not in KNOWN_EXTENSIONS:
                continue
            file_path = os.path.join(path, root, f)
            to_register.append(file_path)
    with Pool(NUM_WORKERS) as p:
        p.map(register_song, to_register)


def score_match(offsets):
    """Score a matched song.

    Calculates a histogram of the deltas between the time offsets of the hashes from the
    recorded sample and the time offsets of the hashes matched in the database for a song.
    The function then returns the size of the largest bin in this histogram as a score.


    """
    tks = list(map(lambda x: x[0] - x[1], offsets))
    hist, _ = np.histogram(tks)
    return np.max(hist)


def best_match(matches):
    """

    Scores each song in the matches dictionary and then returns the song_id with the best score.


    """
    matched_song = None
    best_score = 0
    for song_id, offsets in matches.items():
        if len(offsets) < best_score:
            # can't be best score, avoid expensive histogram
            continue
        score = score_match(offsets)
        if score > best_score:
            best_score = score
            matched_song = song_id
    print(best_score, "best score")
    return matched_song


def recognise_song(filename):

    hashes = fingerprint_file(filename)
    matches = get_matches(hashes)
    matched_song = best_match(matches)
    info = get_info_for_song_id(matched_song)
    if info is not None:
        return info
    return matched_song
