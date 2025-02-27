import os
import json
import mutagen
from mutagen.easyid3 import EasyID3

C418_DIR = "C418"
manifest = {"albums": []}

# Iterate through each album folder in C418/
for album_folder in sorted(os.listdir(C418_DIR)):
    album_path = os.path.join(C418_DIR, album_folder)
    if not os.path.isdir(album_path):
        continue  # skip files if any are in C418/
    
    album_data = {
        "name": album_folder,  # e.g. "C418 - 0x10c"
        "cover": None,
        "songs": []
    }

    # Look for covers and mp3s
    for filename in sorted(os.listdir(album_path)):
        filepath = os.path.join(album_path, filename)
        
        # Cover image
        if filename.lower().startswith("cover") and filename.lower().endswith((".png", ".jpg")):
            album_data["cover"] = os.path.join(C418_DIR, album_folder, filename)
        
        # MP3 files
        elif filename.lower().endswith(".mp3"):
            full_mp3_path = os.path.join(C418_DIR, album_folder, filename)

            # Attempt to read ID3 tags for a title
            song_title = filename.replace(".mp3", "")  # fallback
            try:
                audio = mutagen.File(filepath, easy=True)
                # If there's a title tag, use it
                if audio and "title" in audio:
                    song_title = audio["title"][0]
            except Exception:
                pass  # fallback to filename if reading fails

            album_data["songs"].append({
                "title": song_title,
                "file": full_mp3_path
            })

    # Only add the album if it has songs
    if album_data["songs"]:
        manifest["albums"].append(album_data)

# Write out the manifest
with open("manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print("✅ Manifest generated successfully with ID3-based titles!")
