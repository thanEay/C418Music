import os
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TRCK

# Get the script's directory (repo root)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the base directory containing albums
BASE_DIR = os.path.join(SCRIPT_DIR, "C418")

# Path to manifest.json in the repo root
MANIFEST_PATH = os.path.join(SCRIPT_DIR, "manifest.json")

# Delete existing manifest.json if it exists
if os.path.exists(MANIFEST_PATH):
    os.remove(MANIFEST_PATH)

# Scan for albums and songs
manifest = {"albums": []}

for album_folder in sorted(os.listdir(BASE_DIR)):
    album_path = os.path.join(BASE_DIR, album_folder)

    if not os.path.isdir(album_path):
        continue  # Skip if not a folder

    # Remove "C418 - " from album name if present
    album_name = album_folder.replace("C418 - ", "", 1)

    album_data = {
        "name": album_name,
        "cover": f"C418/{album_folder}/cover.png",
        "songs": []
    }

    for song_file in sorted(os.listdir(album_path)):
        if song_file.lower().endswith(".mp3"):
            song_path = os.path.join(album_path, song_file)

            # Extract metadata
            try:
                audio = MP3(song_path, ID3=ID3)
                title = audio.tags.get("TIT2", TIT2(encoding=3, text=os.path.splitext(song_file)[0])).text[0]
                track = audio.tags.get("TRCK", TRCK(encoding=3, text="0")).text[0]
                
                # Remove track numbers from title
                title = title.lstrip("0123456789.- ")

            except Exception:
                title = os.path.splitext(song_file)[0]  # Fallback to filename

            album_data["songs"].append({
                "title": title,
                "path": f"C418/{album_folder}/{song_file}"
            })

    manifest["albums"].append(album_data)

# Write the manifest.json file in the repo root
with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=4)

print("✅ Manifest created successfully at", MANIFEST_PATH)
