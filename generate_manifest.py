import os
import json

BASE_PATH = "C418"

manifest = {"albums": []}

# Iterate through the C418 folder
for album in sorted(os.listdir(BASE_PATH)):
    album_path = os.path.join(BASE_PATH, album)
    if not os.path.isdir(album_path):
        continue  # Skip files, only process directories

    album_data = {"name": album, "cover": None, "songs": []}

    for file in sorted(os.listdir(album_path)):
        file_path = f"{BASE_PATH}/{album}/{file}"
        if file.lower().startswith("cover") and file.lower().endswith((".png", ".jpg")):
            album_data["cover"] = file_path
        elif file.endswith(".mp3"):
            song_title = file.split(" - ", 2)[-1].replace(".mp3", "").strip()
            album_data["songs"].append({"title": song_title, "file": file_path})

    if album_data["songs"]:  # Only add if there are songs
        manifest["albums"].append(album_data)

# Save the manifest file
with open("manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("✅ Manifest generated successfully!")
