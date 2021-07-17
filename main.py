import json
import os
from detecttunes.recognise import recognise_song

# print(os.getcwd())

TEST_DIR = "recordedaudio/"
print(os.listdir(TEST_DIR))

"""
1. this code is used for testing 
2. music fie in wav format compare with database fingerprint

correct = 0
for song in os.listdir(TEST_DIR):
    print(correct)
    result = new_recognise_song(TEST_DIR + song)
    print(result)

    result_title = result[2]
    #song name contain recorded song name in this case it contain music name
    if result_title == song:
        correct += 1
        print(correct)
    else:
        print(f"{song} - {result_title}")
    print("--------")
print(f"{correct}/{len(os.listdir(TEST_DIR))}")"""

correct = 0

for song in os.listdir(TEST_DIR):
    result = recognise_song(TEST_DIR + song)
    print("Artist , Album   , Title  ")
    print(result)
    print(type(result))
    jsonObj = json.dumps(result)
    print(jsonObj)
    print(type(jsonObj))