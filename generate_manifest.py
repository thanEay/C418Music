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
        "album": "",  # Added album field
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
                if 'TALB' in audio.tags:
                    metadata["album"] = str(audio.tags['TALB'])
            metadata["duration"] = int(audio.info.length)
        elif file_ext == '.flac':
            audio = FLAC(file_path)
            if 'title' in audio:
                metadata["title"] = audio['title'][0]
            if 'artist' in audio:
                metadata["artist"] = audio['artist'][0]
            if 'album' in audio:
                metadata["album"] = audio['album'][0]
            metadata["duration"] = int(audio.info.length)
        elif file_ext == '.ogg':
            audio = OggVorbis(file_path)
            if 'title' in audio:
                metadata["title"] = audio['title'][0]
            if 'artist' in audio:
                metadata["artist"] = audio['artist'][0]
            if 'album' in audio:
                metadata["album"] = audio['album'][0]
            metadata["duration"] = int(audio.info.length)
    except Exception as e:
        print(f"Error reading metadata from {file_path}: {e}")

    return metadata
    
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

def process_study_album(manifest):
    """
    Process the 'study' special album by grouping songs by their original albums.
    """
    # Find the study album in the manifest
    study_album = None
    for album in manifest["albums"]:
        if album["title"].lower() == "study":
            study_album = album
            break
    
    if not study_album:
        return  # No study album found
    
    # Group tracks by original album using metadata
    tracks_by_album = {}
    for track in study_album["tracks"]:
        # Try to extract album info from metadata
        album_name = "Unknown"
        try:
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), track["path"])
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.mp3':
                from mutagen.mp3 import MP3
                audio = MP3(file_path)
                if audio.tags and 'TALB' in audio.tags:
                    album_name = str(audio.tags['TALB'])
            elif file_ext == '.flac':
                from mutagen.flac import FLAC
                audio = FLAC(file_path)
                if 'album' in audio:
                    album_name = audio['album'][0]
            elif file_ext == '.ogg':
                from mutagen.oggvorbis import OggVorbis
                audio = OggVorbis(file_path)
                if 'album' in audio:
                    album_name = audio['album'][0]
        except Exception as e:
            print(f"Error reading album metadata from {track['path']}: {e}")
        
        if album_name not in tracks_by_album:
            tracks_by_album[album_name] = []
        
        tracks_by_album[album_name].append(track)
    
    # Sort by album name and replace study album tracks with sorted list
    sorted_tracks = []
    for album_name in sorted(tracks_by_album.keys()):
        sorted_tracks.extend(tracks_by_album[album_name])
    
    # Update the study album tracks
    study_album["tracks"] = sorted_tracks

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
    
    # Process special study album if it exists
    process_study_album(manifest)
    
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
