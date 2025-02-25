document.addEventListener('DOMContentLoaded', () => {
    // State variables
    let manifest;
    let currentAlbum = null;
    let currentSongIndex = -1;
    let shuffle = false;
    let repeatMode = "off"; // Modes: "off", "all", "one"
  
    // DOM Elements
    const audio = document.getElementById('audio');
    const albumsContainer = document.getElementById('albums-container');
    const songsContainer = document.getElementById('songs-container');
    const albumTitleElem = document.getElementById('album-title');
    const nowPlayingElem = document.getElementById('now-playing');
    const playBtn = document.getElementById('play-btn');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const shuffleBtn = document.getElementById('shuffle-btn');
    const repeatBtn = document.getElementById('repeat-btn');
    const searchInput = document.getElementById('search');
    const themeToggle = document.getElementById('theme-toggle');
  
    // Load manifest.json
    fetch('manifest.json')
      .then(response => response.json())
      .then(data => {
        manifest = data;
        displayAlbums();
      })
      .catch(err => {
        console.error('Error loading manifest:', err);
      });
  
    // Render album list
    function displayAlbums() {
      albumsContainer.innerHTML = '';
      manifest.albums.forEach((album, index) => {
        const albumDiv = document.createElement('div');
        albumDiv.classList.add('album');
        albumDiv.dataset.index = index;
  
        const img = document.createElement('img');
        img.src = album.cover;
        img.alt = album.name;
  
        const nameDiv = document.createElement('div');
        nameDiv.classList.add('album-name');
        nameDiv.textContent = album.name;
  
        albumDiv.appendChild(img);
        albumDiv.appendChild(nameDiv);
  
        albumDiv.addEventListener('click', () => {
          selectAlbum(index);
        });
  
        albumsContainer.appendChild(albumDiv);
      });
    }
  
    // Select an album and display its songs
    function selectAlbum(index) {
      currentAlbum = manifest.albums[index];
      albumTitleElem.textContent = currentAlbum.name;
      currentSongIndex = -1;
      displaySongs(currentAlbum.songs);
    }
  
    // Display songs with optional search filtering
    function displaySongs(songs) {
      const filter = searchInput.value.toLowerCase();
      songsContainer.innerHTML = '';
      songs.forEach((song, index) => {
        if (song.title.toLowerCase().includes(filter)) {
          const songDiv = document.createElement('div');
          songDiv.classList.add('song');
          songDiv.textContent = song.title;
          songDiv.dataset.index = index;
          songDiv.addEventListener('click', () => {
            playSong(index);
          });
          songsContainer.appendChild(songDiv);
        }
      });
    }
  
    // Play a selected song
    function playSong(index) {
      if (!currentAlbum) return;
      currentSongIndex = index;
      const song = currentAlbum.songs[currentSongIndex];
      audio.src = song.file;
      audio.play();
      nowPlayingElem.textContent = `Now Playing: ${song.title} from ${currentAlbum.name}`;
      playBtn.textContent = 'Pause';
      updateSongHighlight();
    }
  
    // Highlight the currently playing song in the list
    function updateSongHighlight() {
      const songDivs = document.querySelectorAll('.song');
      songDivs.forEach(div => {
        if (parseInt(div.dataset.index) === currentSongIndex) {
          div.classList.add('active');
        } else {
          div.classList.remove('active');
        }
      });
    }
  
    // Control button events
    playBtn.addEventListener('click', () => {
      if (audio.paused) {
        audio.play();
        playBtn.textContent = 'Pause';
      } else {
        audio.pause();
        playBtn.textContent = 'Play';
      }
    });
  
    prevBtn.addEventListener('click', playPrevious);
    nextBtn.addEventListener('click', playNext);
  
    shuffleBtn.addEventListener('click', () => {
      shuffle = !shuffle;
      shuffleBtn.textContent = shuffle ? 'Shuffle On' : 'Shuffle Off';
    });
  
    // Cycle repeat modes: off -> all -> one -> off...
    repeatBtn.addEventListener('click', () => {
      if (repeatMode === "off") {
        repeatMode = "all";
        repeatBtn.textContent = 'Repeat All';
      } else if (repeatMode === "all") {
        repeatMode = "one";
        repeatBtn.textContent = 'Repeat One';
      } else {
        repeatMode = "off";
        repeatBtn.textContent = 'Repeat Off';
      }
    });
  
    // When the audio ends, decide what to do next based on repeat mode
    audio.addEventListener('ended', () => {
      if (repeatMode === "one") {
        audio.currentTime = 0;
        audio.play();
      } else {
        playNext();
      }
    });
  
    // Keyboard shortcuts (avoid interfering with text inputs)
    document.addEventListener('keydown', (e) => {
      if (e.target.tagName.toLowerCase() === 'input') return;
      switch (e.code) {
        case 'Space':
          e.preventDefault();
          if (audio.paused) {
            audio.play();
            playBtn.textContent = 'Pause';
          } else {
            audio.pause();
            playBtn.textContent = 'Play';
          }
          break;
        case 'ArrowRight':
          playNext();
          break;
        case 'ArrowLeft':
          playPrevious();
          break;
        case 'KeyS':
          shuffle = !shuffle;
          shuffleBtn.textContent = shuffle ? 'Shuffle On' : 'Shuffle Off';
          break;
        case 'KeyR':
          if (repeatMode === "off") {
            repeatMode = "all";
            repeatBtn.textContent = 'Repeat All';
          } else if (repeatMode === "all") {
            repeatMode = "one";
            repeatBtn.textContent = 'Repeat One';
          } else {
            repeatMode = "off";
            repeatBtn.textContent = 'Repeat Off';
          }
          break;
        default:
          break;
      }
    });
  
    // Update song list based on search query
    searchInput.addEventListener('input', () => {
      if (currentAlbum) {
        displaySongs(currentAlbum.songs);
      }
    });
  
    // Function to play the next song
    function playNext() {
      if (!currentAlbum) return;
      let nextIndex;
      if (shuffle) {
        nextIndex = Math.floor(Math.random() * currentAlbum.songs.length);
      } else {
        nextIndex = currentSongIndex + 1;
        if (nextIndex >= currentAlbum.songs.length) {
          if (repeatMode === "all") {
            nextIndex = 0;
          } else {
            // End of album—do nothing if repeat is off
            return;
          }
        }
      }
      playSong(nextIndex);
    }
  
    // Function to play the previous song
    function playPrevious() {
      if (!currentAlbum) return;
      let prevIndex;
      if (shuffle) {
        prevIndex = Math.floor(Math.random() * currentAlbum.songs.length);
      } else {
        prevIndex = currentSongIndex - 1;
        if (prevIndex < 0) {
          if (repeatMode === "all") {
            prevIndex = currentAlbum.songs.length - 1;
          } else {
            return;
          }
        }
      }
      playSong(prevIndex);
    }
  
    // Toggle light/dark theme
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('dark-theme');
    });
  });
  