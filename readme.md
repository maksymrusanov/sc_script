# SoundCloud Likes to Spotify Playlist

This script automatically collects tracks you've liked on SoundCloud and creates a playlist with them on Spotify.

---

## How It Works

1. Uses Selenium to load your SoundCloud likes page and scrolls to the bottom to load all tracks.
2. Parses the HTML to extract artist names and track titles.
3. Uses the Spotify API to create a new playlist and add the found tracks to it.

---

## Requirements

- Python 3.8+
- Google Chrome and matching ChromeDriver (in your PATH)
- SoundCloud and Spotify accounts
- A registered Spotify app with Client ID, Client Secret, and Redirect URI

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/max1mrusanov/soundclound_script.git
   cd soundclound_script

python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

pip install -r requirements.txt

SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=your_redirect_uri

python src/main.py
