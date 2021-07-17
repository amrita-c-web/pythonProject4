from collections import defaultdict
from detecttunes.fingerprint import fingerprint_file
from detecttunes.recognise import get_info_for_song_id
import numpy as np
from detecttunes.storage import get_cursor


# this code file is used for main first try
def second_match(offsets, fname, supposed):
    tks = list(map(lambda x: x[0] - x[1], offsets))
    # number of matches in highest peak
    hist, _ = np.histogram(tks)
    # plt.plot(_[:-1], hist)
    # plt.title(fname)
    # plt.show()
    return np.max(hist)


def new_get_matches(hashes, threshold=5):
    conn, c = get_cursor()
    h_dict = {}
    for h, t, _ in hashes:
        h_dict[h] = t
    in_values = f"({','.join([str(h[0]) for h in hashes])})"
    c.execute(f"SELECT hash, offset, song_id FROM hash WHERE hash IN {in_values}")
    results = c.fetchall()
    result_dict = defaultdict(list)
    for r in results:
        result_dict[r[2]].append((r[1], h_dict[r[0]]))
    return result_dict


def new_recognise_song(filename):
    hashes = fingerprint_file(filename)
    matches = new_get_matches(hashes)

    matched_song = None
    best_score = 0

    print(f"Recognising {filename} ---")
    for song_id, offsets in matches.items():
        score = second_match(offsets, song_id, filename.split("/")[-1])
        # print("song_id with score")
        # print(f"{song_id} - {score}")
        if score > best_score:
            best_score = score
            matched_song = song_id
    info = get_info_for_song_id(matched_song)
    print(best_score)
    if info is not None:
        return info
