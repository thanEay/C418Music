import os
import json
import argparse
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis

def get_metadata(file_path):
    """Extract metadata from audio files."""
    file_ext = os.path.splitext(file_path)[1].lower()
    metadata = {
        "path": file_path,
        "title": os.path.basename(file_path),
        "artist": "C418",
        "duration": 0
    }
    
    try:
        if file_ext == '.mp3':
            audio = MP3(file_path)
            if audio.tags:
                if 'TIT2' in audio.tags:
                    metadata["title"] = str(audio.tags['TIT2'])
                if 'TPE1' in audio.tags:
                    metadata["artist"] = str(audio.tags['TPE1'])
            metadata["duration"] = int(audio.info.length)
        elif file_ext == '.flac':
            audio = FLAC(file_path)
            if 'title' in audio:
                metadata["title"] = audio['title'][0]
            if 'artist' in audio:
                metadata["artist"] = audio['artist'][0]
            metadata["duration"] = int(audio.info.length)
        elif file_ext == '.ogg':
            audio = OggVorbis(file_path)
            if 'title' in audio:
                metadata["title"] = audio['title'][0]
            if 'artist' in audio:
                metadata["artist"] = audio['artist'][0]
            metadata["duration"] = int(audio.info.length)
    except Exception as e:
        print(f"Error reading metadata from {file_path}: {e}")
    
    return metadata

def scan_directory():
    """
    Scan the current directory and all subdirectories for audio files and album covers.
    Generate a manifest.json file with the results.
    """
    audio_extensions = ['.mp3', '.flac', '.ogg', '.wav']
    cover_filenames = ['cover.png', 'cover.jpg', 'folder.jpg', 'album.jpg']
    
    # Root is the current directory where the script is run
    root_dir = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.join(root_dir, "manifest.json")
    
    # Structure for our manifest
    manifest = {
        "albums": [],
        "lastUpdated": None
    }
    
    # Find all directories that contain audio files (potential albums)
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip the root directory itself as an album
        if dirpath == root_dir:
            continue
        
        # Check if this directory contains audio files
        audio_files = [f for f in filenames if os.path.splitext(f)[1].lower() in audio_extensions]
        if not audio_files:
            continue
        
        # This is a potential album, get its data
        relative_path = os.path.relpath(dirpath, root_dir)
        
        # Extract album name from directory name, removing "C418 - " if present
        album_name = os.path.basename(dirpath)
        if album_name.startswith("C418 - "):
            album_name = album_name[7:]
        
        # Find cover image if it exists
        cover_image = None
        for cover in cover_filenames:
            cover_path = os.path.join(dirpath, cover)
            if os.path.exists(cover_path):
                cover_image = os.path.join(relative_path, cover)
                break
        
        # Get track metadata
        tracks = []
        for audio_file in audio_files:
            file_path = os.path.join(dirpath, audio_file)
            metadata = get_metadata(file_path)
            metadata["path"] = os.path.join(relative_path, audio_file)
            tracks.append(metadata)
        
        # Sort tracks by filename if no track number in metadata
        tracks.sort(key=lambda x: x["path"])
        
        album_data = {
            "title": album_name,
            "path": relative_path,
            "cover": cover_image,
            "tracks": tracks
        }
        
        manifest["albums"].append(album_data)
    
    # Sort albums alphabetically
    manifest["albums"].sort(key=lambda x: x["title"])
    
    # Add last updated timestamp
    import datetime
    manifest["lastUpdated"] = datetime.datetime.now().isoformat()
    
    # Write manifest to file
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"Manifest file created at: {manifest_path}")
    print(f"Found {len(manifest['albums'])} albums with a total of {sum(len(album['tracks']) for album in manifest['albums'])} tracks.")

if __name__ == "__main__":
    try:
        import mutagen
    except ImportError:
        print("The mutagen library is required. Please install it using:")
        print("pip install mutagen")
        exit(1)
        
    scan_directory()