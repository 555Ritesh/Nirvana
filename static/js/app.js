const clientID = '2ab8b140e3ec4f018f8bd9f4aa686302'; 
const clientSecret = '62c215c84e914ebea35c58b31a59e2f6'; 

let accessToken = '';
let cameraStream = null;

// Add functions to handle user authentication and song interactions
let isUserLoggedIn = false;
let currentUser = null;

// Check if the user is logged in when the page loads
function checkUserAuthentication() {
    const token = getCookie('token');
    if (token) {
        isUserLoggedIn = true;
        // Add logout button to navbar if not already there
        addLogoutToNavbar();
    } else {
        window.location.href = '/login';
    }
}

// Get a cookie by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Add logout button to navbar
function addLogoutToNavbar() {
    const navbar = document.querySelector('.navbar-nav');
    if (navbar && !document.getElementById('logout-link')) {
        const dashboardItem = document.createElement('li');
        dashboardItem.classList.add('nav-item');
        const dashboardLink = document.createElement('a');
        dashboardLink.classList.add('nav-link');
        dashboardLink.href = '/dashboard';
        dashboardLink.textContent = 'Dashboard';
        dashboardItem.appendChild(dashboardLink);
        
        const logoutItem = document.createElement('li');
        logoutItem.classList.add('nav-item');
        const logoutLink = document.createElement('a');
        logoutLink.classList.add('nav-link');
        logoutLink.href = '#';
        logoutLink.id = 'logout-link';
        logoutLink.textContent = 'Logout';
        logoutLink.addEventListener('click', handleLogout);
        logoutItem.appendChild(logoutLink);
        
        navbar.appendChild(dashboardItem);
        navbar.appendChild(logoutItem);
    }
}

// Handle logout
async function handleLogout(e) {
    e.preventDefault();
    
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
            window.location.href = '/login';
        } else {
            alert(data.message || 'Failed to logout');
        }
    } catch (error) {
        console.error('Error logging out:', error);
        alert('An error occurred during logout');
    }
}

// Toggle like status for a song
async function toggleLike(trackId, songName, artistName, albumImageUrl) {
    if (!isUserLoggedIn) {
        window.location.href = '/login';
        return;
    }
    
    try {
        const response = await fetch('/api/songs/like', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                track_id: trackId,
                song_name: songName,
                artist_name: artistName,
                album_image_url: albumImageUrl
            })
        });
        
        const data = await response.json();
        
        // Update UI based on like status
        const likeButtons = document.querySelectorAll(`.like-btn[data-track-id="${trackId}"]`);
        likeButtons.forEach(button => {
            if (data.liked) {
                button.classList.add('active');
                button.innerHTML = '❤️';
            } else {
                button.classList.remove('active');
                button.innerHTML = '♡';
            }
        });
        
        return data.liked;
    } catch (error) {
        console.error('Error toggling like:', error);
        return null;
    }
}

// Toggle save status for a song
async function toggleSave(trackId, songName, artistName, albumImageUrl) {
    if (!isUserLoggedIn) {
        window.location.href = '/login';
        return;
    }
    
    try {
        const response = await fetch('/api/songs/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                track_id: trackId,
                song_name: songName,
                artist_name: artistName,
                album_image_url: albumImageUrl
            })
        });
        
        const data = await response.json();
        
        // Update UI based on save status
        const saveButtons = document.querySelectorAll(`.save-btn[data-track-id="${trackId}"]`);
        saveButtons.forEach(button => {
            if (data.saved) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
        
        return data.saved;
    } catch (error) {
        console.error('Error toggling save:', error);
        return null;
    }
}

// Add song to listening history
async function addToHistory(trackId, songName, artistName, albumImageUrl) {
    if (!isUserLoggedIn) return;
    
    try {
        await fetch('/api/songs/history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                track_id: trackId,
                song_name: songName,
                artist_name: artistName,
                album_image_url: albumImageUrl
            })
        });
    } catch (error) {
        console.error('Error adding to history:', error);
    }
}

// Function to get the access token from Spotify
function getAccessToken() {
    const auth = btoa(`${clientID}:${clientSecret}`);
    
    fetch('https://accounts.spotify.com/api/token', {
        method: 'POST',
        headers: {
            'Authorization': `Basic ${auth}`,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'grant_type=client_credentials',
    })
    .then(response => response.json())
    .then(data => {
        accessToken = data.access_token;
        console.log('Access Token:', accessToken);
    })
    .catch(error => console.error('Error getting access token:', error));
}

// Toggle like/save state in localStorage
function toggleTrackState(trackId, stateType, button) {
    let savedTracks = JSON.parse(localStorage.getItem(stateType)) || {};
    if (savedTracks[trackId]) {
        delete savedTracks[trackId];
        button.classList.remove('active');
        
        // Change the emoji if it's a like button
        if (stateType === 'likedTracks') {
            button.innerHTML = '♡';
        }
    } else {
        savedTracks[trackId] = true;
        button.classList.add('active');
        
        // Change the emoji if it's a like button
        if (stateType === 'likedTracks') {
            button.innerHTML = '❤️';
        }
    }
    localStorage.setItem(stateType, JSON.stringify(savedTracks));
}

// Create like and save buttons container
function createTrackActions(trackId, isImageOverlay = false) {
    const actionsDiv = document.createElement('div');
    actionsDiv.classList.add('track-actions');
    if (isImageOverlay) {
        actionsDiv.classList.add('image-overlay-actions');
    } else {
        actionsDiv.classList.add('button-actions');
    }

    const likeButton = document.createElement('button');
    likeButton.title = 'Like';
    likeButton.classList.add('like-btn');
    likeButton.onclick = (e) => {
        e.stopPropagation();
        toggleTrackState(trackId, 'likedTracks', likeButton);
    };

    const saveButton = document.createElement('button');
    saveButton.innerHTML = '💾'; // Floppy disk symbol for save
    saveButton.title = 'Save';
    saveButton.classList.add('save-btn');
    saveButton.onclick = (e) => {
        e.stopPropagation();
        toggleTrackState(trackId, 'savedTracks', saveButton);
    };

    // Set initial active state from localStorage
    const likedTracks = JSON.parse(localStorage.getItem('likedTracks')) || {};
    const savedTracks = JSON.parse(localStorage.getItem('savedTracks')) || {};
    
    if (likedTracks[trackId]) {
        likeButton.classList.add('active');
        likeButton.innerHTML = '❤️'; // Filled heart for liked
    } else {
        likeButton.innerHTML = '♡'; // Empty heart for not liked
    }
    
    if (savedTracks[trackId]) {
        saveButton.classList.add('active');
    }

    actionsDiv.appendChild(likeButton);
    if (!isImageOverlay) {
        actionsDiv.appendChild(saveButton);
    }

    return { actionsDiv, saveButton };
}

// Display search results on the page
function displayResults(data) {
    const resultsList = document.getElementById('results-list');
    resultsList.innerHTML = '';

    if (data.tracks && data.tracks.items.length > 0) {
        // Limit to maximum 10 tracks
        const tracksToDisplay = data.tracks.items.slice(0, 10);
        
        tracksToDisplay.forEach((track) => {
            const trackCard = document.createElement('div');
            trackCard.classList.add('track-card');

            const imageContainer = document.createElement('div');
            imageContainer.classList.add('image-container');

            const albumImage = document.createElement('img');
            albumImage.src = track.album.images[0]?.url || 'default-placeholder.png';
            albumImage.alt = 'Album Image';
            albumImage.classList.add('album-cover');

            // Create like button overlay for image
            const likeButton = document.createElement('button');
            likeButton.classList.add('like-btn');
            likeButton.setAttribute('data-track-id', track.id);
            likeButton.innerHTML = track.is_liked ? '❤️' : '♡';
            if (track.is_liked) likeButton.classList.add('active');
            likeButton.onclick = (e) => {
                e.stopPropagation();
                toggleLike(track.id, track.name, track.artists[0].name, track.album.images[0]?.url);
            };
            
            const imageActions = document.createElement('div');
            imageActions.classList.add('image-overlay-actions');
            imageActions.appendChild(likeButton);
            
            imageContainer.appendChild(albumImage);
            imageContainer.appendChild(imageActions);

            const contentArea = document.createElement('div');
            contentArea.classList.add('content-area');

            const trackTitle = document.createElement('p');
            trackTitle.classList.add('title');
            trackTitle.textContent = track.name;

            const artistName = document.createElement('p');
            artistName.classList.add('artist');
            artistName.textContent = track.artists[0].name;

            const playButton = document.createElement('button');
            playButton.classList.add('play-preview-btn');
            if (track.preview_url) {
                playButton.textContent = 'Play Preview';
                playButton.onclick = () => {
                    playTrack(track.preview_url, track.name, track.id, track.artists[0].name, track.album.images[0]?.url);
                };
            } else {
                playButton.style.display = 'none';  // Hide the button if no preview URL exists
            }

            contentArea.appendChild(trackTitle);
            contentArea.appendChild(artistName);
            contentArea.appendChild(playButton);

            const buttonContainer = document.createElement('div');
            buttonContainer.classList.add('button-container');

            const spotifyLink = document.createElement('a');
            spotifyLink.href = `https://open.spotify.com/track/${track.id}`;
            spotifyLink.target = "_blank";
            spotifyLink.textContent = 'Open';
            spotifyLink.classList.add('btn', 'btn-success');
            spotifyLink.onclick = (e) => {
                // Add to history when opening in Spotify
                addToHistory(track.id, track.name, track.artists[0].name, track.album.images[0]?.url);
            };

            // Add save button next to spotify link
            const saveButton = document.createElement('button');
            saveButton.classList.add('save-btn');
            saveButton.setAttribute('data-track-id', track.id);
            saveButton.innerHTML = '💾';
            if (track.is_saved) saveButton.classList.add('active');
            saveButton.onclick = (e) => {
                e.stopPropagation();
                toggleSave(track.id, track.name, track.artists[0].name, track.album.images[0]?.url);
            };
            
            buttonContainer.appendChild(saveButton);
            buttonContainer.appendChild(spotifyLink);

            trackCard.appendChild(imageContainer);
            trackCard.appendChild(contentArea);
            trackCard.appendChild(buttonContainer);
            
            resultsList.appendChild(trackCard);
        });
    } else {
        resultsList.innerHTML = '<p>No tracks found. Try another search term.</p>';
    }
}

// Play track preview
function playTrack(url, trackName, trackId, artistName, albumImageUrl) {
    const audioPlayer = document.getElementById('audio-player');
    audioPlayer.src = url;
    audioPlayer.play();
    alert(`Playing: ${trackName}`);
    // Add to history when playing
    addToHistory(trackId, trackName, artistName, albumImageUrl);
}

// Recommend songs based on selected mood and language
function recommendSongs() {
    const mood = document.getElementById('mood-select').value;
    const language = document.getElementById('language-select').value;

    fetch(`http://127.0.0.1:5001/recommend?mood=${mood}&language=${language}&limit=10`)
        .then(response => response.json())
        .then(data => displayRecommendations(data))
        .catch(error => {
            console.error('Error fetching recommendations:', error);
            alert('Failed to fetch recommendations. Please try again.');
        });
}

// Display the recommended songs as cards with album image, song name, artist, and Spotify link
function displayRecommendations(songs) {
    const existingContainer = document.getElementById("recommendations-container");
    if (existingContainer) {
        existingContainer.remove();
    }
    
    const recommendationsContainer = document.createElement("div");
    recommendationsContainer.id = "recommendations-container";
    
    document.querySelector(".container").appendChild(recommendationsContainer);

    if (!songs || songs.length === 0) {
        recommendationsContainer.innerHTML = "<p>No recommendations available.</p>";
        return;
    }

    // Limit to maximum 10 songs
    const songsToDisplay = songs.slice(0, 10);

    songsToDisplay.forEach(song => {
        const card = document.createElement("div");
        card.classList.add("track-card");

        fetch(`https://api.spotify.com/v1/tracks/${song.track_id}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Accept': 'application/json'
            }
        })
        .then(response => response.json())
        .then(trackData => {
            const imageContainer = document.createElement('div');
            imageContainer.classList.add('image-container');

            const albumImage = document.createElement("img");
            albumImage.classList.add("album-cover");
            albumImage.src = trackData.album.images[0]?.url || 'default-placeholder.png';
            albumImage.alt = "Album Image";
            
            // Add album image URL to the song object for later use
            song.album_image_url = trackData.album.images[0]?.url;

            // Create like button overlay for image
            const likeButton = document.createElement('button');
            likeButton.classList.add('like-btn');
            likeButton.setAttribute('data-track-id', song.track_id);
            likeButton.innerHTML = song.is_liked ? '❤️' : '♡';
            if (song.is_liked) likeButton.classList.add('active');
            likeButton.onclick = (e) => {
                e.stopPropagation();
                toggleLike(song.track_id, song.song_name, song.singer, song.album_image_url);
            };
            
            const imageActions = document.createElement('div');
            imageActions.classList.add('image-overlay-actions');
            imageActions.appendChild(likeButton);
            
            imageContainer.appendChild(albumImage);
            imageContainer.appendChild(imageActions);

            const contentArea = document.createElement('div');
            contentArea.classList.add('content-area');

            const title = document.createElement("p");
            title.classList.add('title');
            title.textContent = song.song_name;

            const artist = document.createElement("p");
            artist.classList.add('artist');
            artist.textContent = song.singer;

            // Add Play Preview button if preview URL exists
            if (trackData.preview_url) {
                const playButton = document.createElement('button');
                playButton.classList.add('play-preview-btn');
                playButton.textContent = 'Play Preview';
                playButton.onclick = () => {
                    playTrack(trackData.preview_url, song.song_name, song.track_id, song.singer, song.album_image_url);
                    // Add to history with album image
                    addToHistory(song.track_id, song.song_name, song.singer, song.album_image_url);
                };
                contentArea.appendChild(title);
                contentArea.appendChild(artist);
                contentArea.appendChild(playButton);
            } else {
                contentArea.appendChild(title);
                contentArea.appendChild(artist);
            }

            const buttonContainer = document.createElement('div');
            buttonContainer.classList.add('button-container');

            const spotifyLink = document.createElement("a");
            spotifyLink.href = `https://open.spotify.com/track/${song.track_id}`;
            spotifyLink.target = "_blank";
            spotifyLink.textContent = "Open";
            spotifyLink.classList.add("btn", "btn-success");
            spotifyLink.onclick = (e) => {
                // Add to history when opening in Spotify
                addToHistory(song.track_id, song.song_name, song.singer, song.album_image_url);
            };

            // Add save button next to spotify link
            const saveButton = document.createElement('button');
            saveButton.classList.add('save-btn');
            saveButton.setAttribute('data-track-id', song.track_id);
            saveButton.innerHTML = '💾';
            if (song.is_saved) saveButton.classList.add('active');
            saveButton.onclick = (e) => {
                e.stopPropagation();
                toggleSave(song.track_id, song.song_name, song.singer, song.album_image_url);
            };
            
            buttonContainer.appendChild(saveButton);
            buttonContainer.appendChild(spotifyLink);

            card.appendChild(imageContainer);
            card.appendChild(contentArea);
            card.appendChild(buttonContainer);

            recommendationsContainer.appendChild(card);
        })
        .catch(error => {
            console.error("Error fetching track details:", error);
        });
    });
}

// Function to toggle camera on/off
function toggleCamera() {
  const video = document.getElementById("video");
  const toggleBtn = document.getElementById("toggle-camera-btn");
  
  if (cameraStream) {
    // Turn off camera
    cameraStream.getTracks().forEach(track => track.stop());
    cameraStream = null;
    video.srcObject = null;
    video.style.display = "none";
    toggleBtn.textContent = "Turn Camera On";
    toggleBtn.classList.remove("btn-danger");
    toggleBtn.classList.add("btn-primary");
  } else {
    // Turn on camera
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        cameraStream = stream;
        video.srcObject = stream;
        video.style.display = "block";
        toggleBtn.textContent = "Turn Camera Off";
        toggleBtn.classList.remove("btn-primary");
        toggleBtn.classList.add("btn-danger");
      })
      .catch(error => {
        console.error("Camera access error:", error);
        alert("Could not access camera: " + error.message);
      });
  }
}

window.onload = function () {
    // Check if user is logged in
    checkUserAuthentication();
    
    // Get Spotify access token
    getAccessToken();
    
    // Camera setup
    const video = document.getElementById("video");
    if (video) {
        video.style.display = "none";
    }
    
    // Setup camera toggle button
    const toggleBtn = document.getElementById("toggle-camera-btn");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", toggleCamera);
    }
};

async function captureMood() {
  const canvas = document.getElementById("canvas");
  const video = document.getElementById("video");
  const captureBtn = document.getElementById("capture-btn");
  
  // Show loading state
  captureBtn.disabled = true;
  captureBtn.innerHTML = 'Detecting Mood...';
  
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  const imageDataURL = canvas.toDataURL("image/jpeg");

  try {
    const response = await fetch("/detect-mood", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imageDataURL }),
    });

    const result = await response.json();

    if (result.mood) {
      alert("Detected Mood: " + result.mood);
      document.getElementById("mood-select").value = result.mood;
    } else {
      alert("Error detecting mood: " + result.error);
    }
  } catch (err) {
    console.error("Error sending image to backend:", err);
    alert("Failed to detect mood.");
  } finally {
    // Reset button state
    captureBtn.disabled = false;
    captureBtn.innerHTML = 'Capture Mood';
  }
}

document.getElementById("capture-btn").addEventListener("click", captureMood);

// Search function to search tracks using Spotify API
function search() {
    const searchInput = document.getElementById('search-input').value.trim();
    
    if (!searchInput) {
        alert('Please enter a search term');
        return;
    }

    if (!accessToken) {
        alert('Please wait for Spotify authentication to complete');
        getAccessToken();
        return;
    }

    fetch(`https://api.spotify.com/v1/search?q=${encodeURIComponent(searchInput)}&type=track&limit=10`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Search request failed');
        }
        return response.json();
    })
    .then(data => {
        displayResults(data);
    })
    .catch(error => {
        console.error('Error searching tracks:', error);
        alert('Failed to search tracks. Please try again.');
    });
}
