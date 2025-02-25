import os
import json
import re

manifest = {"albums": []}

# Iterate over directories in the repository root.
# This assumes your album folders (e.g. "C418 - 0x10c", "C418 - 2 years of failure", etc.)
# are at the root level.
for entry in sorted(os.listdir('.')):
    # Skip hidden directories or non-album folders (like .github, node_modules, etc.)
    if entry.startswith('.') or not os.path.isdir(entry):
        continue
    # Only process directories that contain at least one MP3 file
    files = os.listdir(entry)
    if not any(f.lower().endswith('.mp3') for f in files):
        continue

    album_data = {"name": entry, "cover": None, "songs": []}

    for filename in sorted(files):
        filepath = os.path.join(entry, filename)
        # Check for cover image (png or jpg)
        if filename.lower().startswith("cover") and filename.lower().endswith(('.png', '.jpg')):
            album_data["cover"] = filepath
        elif filename.lower().endswith(".mp3"):
            # Split the filename by " - " to isolate the song info.
            # Expected format: "AlbumName - AlbumName - [track number] [Song Title].mp3"
            parts = filename.split(" - ")
            if len(parts) >= 3:
                # Join the parts after the first two (in case the title has dashes)
                song_info = " - ".join(parts[2:])
            else:
                song_info = parts[-1]
            song_info = song_info.replace(".mp3", "").strip()
            # Remove any leading track number (digits followed by optional space)
            song_title = re.sub(r'^\d+\s*', '', song_info)
            album_data["songs"].append({"title": song_title, "file": filepath})

    # Only add albums that have at least one song
    if album_data["songs"]:
        manifest["albums"].append(album_data)

with open("manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("✅ Manifest generated successfully!")
