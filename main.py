#!/usr/bin/env python3
"""
BMBF Python Playlist exporter
--------------
Converts playlist contained inside BMBF's config.json into .bplist playlists
"""

# Dependencies:
# pip3 install requests

import os
import base64
import json
from sys import argv

import requests

BEATSAVER_BYHASH_URL = "https://beatsaver.com/api/maps/by-hash/"
BEATSAVER_CDN_URL = "https://beatsaver.com"
BEATSAVER_HEADERS = {"User-Agent": "BMBF Python Playlist exporter"}

def main():
    """Main function"""

    if len(argv) <= 1 or argv[1].lower() in ["-h", "--help"]:
        print("BMBF Python Playlist exporter\n\tHelps you export your handmade playlists from BMBF to the more common .bplist (aka .json) format")
        print(f"Usage: python3 {argv[0]} [-h] [--help] config.json")
        print("config.json is the configuration file of BMBF, findable under \n\t/sdcard/BMBFData/config.json\n on your Oculus Quest device")
        exit(0)
    config_file = argv[1]

    if not os.path.isfile(config_file):
        print(f"{config_file} doesn't exist")
        exit(1)

    try:
        with open(config_file, "r") as f:
            bmbf_config = json.load(f)
    except json.JSONDecodeError:
        print(f"{config_file} is not a valid JSON file")
        exit(1)

    playlists = bmbf_config["Playlists"]

    if len(playlists) == 0:
        print("No playlists found in config!")
        exit(1)

    print("Playlist available:")

    for i, playlist in enumerate(playlists):
        print(f"\t{i+1} - {playlist['PlaylistName']}")

    choice = "-1"

    while not (choice.isnumeric() and 0 < int(choice) <= len(playlists)):
        choice = input(f"Which playlist do you wish to convert ? [1-{len(playlists)}] ")
    choice = int(choice) - 1
    bmbf_playlist = playlists[choice]

    print(f"Exporting \"{bmbf_playlist['PlaylistName']}\"...")

    choice = input(f"Do you wish to download the songs' covers ? It might increase the resulting filesize to a few megabytes ! yes/[no]")
    download_covers = False if "y" not in choice.lower() else True

    bplist_playlist = convert_playlist(bmbf_playlist, covers=download_covers)

    with open(bmbf_playlist["PlaylistID"] + ".bplist", "w+") as f:
        json.dump(bplist_playlist, f)

    print("Successfully exported !")

def convert_playlist(playlist, covers=True):
    playlist_out = {
                "playlistTitle": playlist["PlaylistName"],
                "playlistAuthor": "BMBF Python Playlist exporter",
                "playlistDescription": f"This playlist was exported from \"{playlist['PlaylistName']}\" initially made on BMBF",
                "songs": [convert_song(song, covers=covers) for song in playlist["SongList"]]
            }

    if os.path.isfile("playlist_cover.png"):
        print("Detected playlist cover under playlist_cover.png, using it...")
        with open("playlist_cover.png", "rb") as cover_image:
            cover_picture = base64.b64encode(cover_image.read()).decode("utf8")
            cover_b64_uri = "data:image/png;base64," + cover_picture
            playlist_out["image"] = cover_b64_uri

    return playlist_out

def convert_song(song, covers=True):
    print(f"\tExporting \"{song['SongName']}\"")
    song_hash = song["SongID"].replace("custom_level_", "").upper()

    song_out = {
        "hash": song_hash,
        "songName": song["SongName"],
    }

    if covers:
        song_out["image"] = download_b64_cover(song_hash)

    return song_out

def download_b64_cover(song_hash):
    try:
        song_record = requests.get(BEATSAVER_BYHASH_URL + song_hash.lower(), headers=BEATSAVER_HEADERS).json()
    except json.JSONDecodeError:
        print(f"Beatsaver API didn't respond correctly, skipping the song's cover download ...")

        return PURPLE_SQUARE_BASE64
    song_name = song_record["metadata"]["songName"]
    print(f"\tDownloading cover picture for \"{song_name}\"")
    cover_url = BEATSAVER_CDN_URL + song_record["coverURL"]
    cover_picture = requests.get(cover_url, headers=BEATSAVER_HEADERS)

    return ("data:" +
        str(cover_picture.headers["Content-Type"]) + ";" +
        "base64," + base64.b64encode(cover_picture.content).decode("utf8"))

PURPLE_SQUARE_BASE64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAEAAQADAREAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAj/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFgEBAQEAAAAAAAAAAAAAAAAAAAcI/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AjdcGkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH//Z"

if __name__ == "__main__":
    main()
