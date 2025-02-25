import os
import json

# Define the base directory (repository root)
base_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize the manifest dictionary
manifest = {'albums': []}

# Traverse the base directory
for album_name in os.listdir(base_dir):
    album_path = os.path.join(base_dir, album_name)
    if os.path.isdir(album_path) and album_name not in ['.git', '__pycache__']:  # Ignore hidden/system directories
        album = {
            'name': album_name,
            'cover': None,
            'songs': []
        }
        for item in os.listdir(album_path):
            item_path = os.path.join(album_path, item)
            if os.path.isfile(item_path):
                if item.lower().endswith(('.mp3', '.wav', '.flac')):
                    song = {
                        'title': os.path.splitext(item)[0],
                        'file': f"{album_name}/{item}",
                        'lyrics': None
                    }
                    # Check for corresponding lyrics file
                    lyrics_file = f"{os.path.splitext(item)[0]}.txt"
                    lyrics_path = os.path.join(album_path, lyrics_file)
                    if os.path.exists(lyrics_path):
                        song['lyrics'] = f"{album_name}/{lyrics_file}"
                    album['songs'].append(song)
                elif item.lower() in ['cover.jpg', 'cover.png']:
                    album['cover'] = f"{album_name}/{item}"
        manifest['albums'].append(album)

# Save the manifest to a JSON file in the repo root
manifest_path = os.path.join(base_dir, 'manifest.json')
with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2)

print('✅ manifest.json has been generated successfully.')
