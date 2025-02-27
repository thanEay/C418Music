document.addEventListener('DOMContentLoaded', () => {
    // State
    let manifest;
    let currentAlbum = null;
    let currentSongIndex = -1;
    let shuffleEnabled = false;
    let repeatEnabled = false;
  
    // DOM references
    const audio = document.getElementById('audio');
    const albumsContainer = document.getElementById('albums-container');
    const songsContainer = document.getElementById('songs-container');
    const albumTitleElem = document.getElementById('album-title');
    const nowPlayingElem = document.getElementById('now-playing');
    const playBtn = document.getElementById('play-btn');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const searchInput = document.getElementById('search');
    const themeToggle = document.getElementById('theme-toggle');
  
    // Shuffle/Repeat checkboxes
    const shuffleCheckbox = document.getElementById('shuffle-checkbox');
    const repeatCheckbox = document.getElementById('repeat-checkbox');
  
    // Progress bar & time
    const progressBar = document.getElementById('progress-bar');
    const currentTimeSpan = document.getElementById('current-time');
    const durationSpan = document.getElementById('duration');
    const songTitleDisplay = document.getElementById('song-title');
  
    // 10s skip
    const forwardBtn = document.getElementById('forward-btn');
    const backwardBtn = document.getElementById('backward-btn');
  
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
  
    function displayAlbums() {
      albumsContainer.innerHTML = '';
      manifest.albums.forEach((album, index) => {
        const albumDiv = document.createElement('div');
        albumDiv.classList.add('album');
        albumDiv.dataset.index = index;
  
        const img = document.createElement('img');
        img.src = album.cover || '';
        img.alt = album.name;
  
        const nameDiv = document.createElement('div');
        nameDiv.classList.add('album-name');
        nameDiv.textContent = album.name;
  
        albumDiv.appendChild(img);
        albumDiv.appendChild(nameDiv);
  
        albumDiv.addEventListener('click', () => selectAlbum(index));
        albumsContainer.appendChild(albumDiv);
      });
    }
  
    function selectAlbum(index) {
      currentAlbum = manifest.albums[index];
      albumTitleElem.textContent = currentAlbum.name;
      currentSongIndex = -1;
      displaySongs(currentAlbum.songs);
    }
  
    function displaySongs(songs) {
      const filter = searchInput.value.toLowerCase();
      songsContainer.innerHTML = '';
      songs.forEach((song, i) => {
        if (song.title.toLowerCase().includes(filter)) {
          const songDiv = document.createElement('div');
          songDiv.classList.add('song');
          songDiv.dataset.index = i;
          songDiv.textContent = song.title;
          songDiv.addEventListener('click', () => playSong(i));
          songsContainer.appendChild(songDiv);
        }
      });
    }
  
    function playSong(index) {
      if (!currentAlbum) return;
      currentSongIndex = index;
      const song = currentAlbum.songs[currentSongIndex];
      audio.src = song.file;
      audio.play();
      nowPlayingElem.textContent = `Now Playing: ${song.title} from ${currentAlbum.name}`;
      songTitleDisplay.textContent = song.title; // bottom bar
      playBtn.textContent = 'Pause';
      updateSongHighlight();
    }
  
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
  
    // Controls
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
  
    // Shuffle/Repeat checkboxes
    shuffleCheckbox.addEventListener('change', () => {
      shuffleEnabled = shuffleCheckbox.checked;
    });
    repeatCheckbox.addEventListener('change', () => {
      repeatEnabled = repeatCheckbox.checked;
    });
  
    // 10s skip
    forwardBtn.addEventListener('click', () => {
      audio.currentTime = Math.min(audio.currentTime + 10, audio.duration);
    });
    backwardBtn.addEventListener('click', () => {
      audio.currentTime = Math.max(audio.currentTime - 10, 0);
    });
  
    // Progress bar events
    audio.addEventListener('loadedmetadata', () => {
      progressBar.max = audio.duration || 0;
      durationSpan.textContent = formatTime(audio.duration);
    });
  
    audio.addEventListener('timeupdate', () => {
      progressBar.value = audio.currentTime;
      currentTimeSpan.textContent = formatTime(audio.currentTime);
    });
  
    progressBar.addEventListener('input', () => {
      audio.currentTime = progressBar.value;
    });
  
    // When song ends, handle repeat/shuffle
    audio.addEventListener('ended', () => {
      if (repeatEnabled) {
        // "Repeat One" style: replay same track
        audio.currentTime = 0;
        audio.play();
      } else {
        // "Repeat All" style is typically separate,
        // but let's keep it simple:
        playNext();
      }
    });
  
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      // Avoid interfering with text input
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
        default:
          break;
      }
    });
  
    // Filter songs
    searchInput.addEventListener('input', () => {
      if (currentAlbum) {
        displaySongs(currentAlbum.songs);
      }
    });
  
    function playNext() {
      if (!currentAlbum) return;
      let nextIndex;
      if (shuffleEnabled) {
        nextIndex = Math.floor(Math.random() * currentAlbum.songs.length);
      } else {
        nextIndex = currentSongIndex + 1;
        if (nextIndex >= currentAlbum.songs.length) {
          // Wrap around if you want "Repeat All" style
          nextIndex = 0;
        }
      }
      playSong(nextIndex);
    }
  
    function playPrevious() {
      if (!currentAlbum) return;
      let prevIndex;
      if (shuffleEnabled) {
        prevIndex = Math.floor(Math.random() * currentAlbum.songs.length);
      } else {
        prevIndex = currentSongIndex - 1;
        if (prevIndex < 0) {
          // Wrap around if you want "Repeat All"
          prevIndex = currentAlbum.songs.length - 1;
        }
      }
      playSong(prevIndex);
    }
  
    function formatTime(sec) {
      if (!sec || isNaN(sec)) return "0:00";
      const m = Math.floor(sec / 60);
      const s = Math.floor(sec % 60);
      return `${m}:${s < 10 ? '0' : ''}${s}`;
    }
  
    // Theme toggle
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('dark-theme');
    });
  });
  