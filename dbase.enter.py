from detecttunes.recognise import register_song
import os

# print(os.getcwd())

# To enter the songs in database run this code


TEST_DIR = "Tests/"
print(os.listdir(TEST_DIR))

for song in os.listdir(TEST_DIR):
    if not register_song((TEST_DIR + song)):
        print("successful")
    else:
        print("false already registered")
