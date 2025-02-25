import os
import json

# Directory that contains all album folders
ALBUMS_DIR = "C418"

manifest = {"albums": []}

# Iterate over subdirectories in the ALBUMS_DIR folder
for album in sorted(os.listdir(ALBUMS_DIR)):
    album_dir = os.path.join(ALBUMS_DIR, album)
    if not os.path.isdir(album_dir):
        continue  # Skip any files in the container folder

    album_data = {"name": album, "cover": None, "songs": []}

    for filename in sorted(os.listdir(album_dir)):
        filepath = os.path.join(ALBUMS_DIR, album, filename)
        # Identify the cover image
        if filename.lower().startswith("cover") and filename.lower().endswith(('.png', '.jpg')):
            album_data["cover"] = filepath
        # Identify MP3 files and extract song title
        elif filename.lower().endswith(".mp3"):
            parts = filename.split(" - ")
            if len(parts) >= 3:
                song_title = " - ".join(parts[2:]).replace(".mp3", "").strip()
            else:
                song_title = filename.replace(".mp3", "").strip()
            album_data["songs"].append({"title": song_title, "file": filepath})
    
    # Add album only if it has at least one song
    if album_data["songs"]:
        manifest["albums"].append(album_data)

with open("manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("✅ Manifest generated successfully!")
