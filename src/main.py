from selenium import webdriver
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
from datetime import datetime
import re
from dotenv import load_dotenv
import os

# ==== Load SoundCloud likes ====
soundclound_script
url = 'https://soundcloud.com/tripple_death/likes'
scroll_pause = 2
max_tries_without_growth = 5

with webdriver.Chrome() as driver:
    driver.get(url)
    driver.maximize_window()
    time.sleep(5)

    last_height = driver.execute_script("return document.body.scrollHeight")
    tries = 0

    while tries < max_tries_without_growth:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            tries += 1
        else:
            tries = 0

        last_height = new_height

    print("Scrolling complete.")

    with open('soundclound_script/html_res.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)

# ==== Parse saved HTML ====#

with open('sc_parser/html_res.html', 'r', encoding='utf-8') as file:
    html = file.read()

soup = BeautifulSoup(html, 'html.parser')

tracks = []
for block in soup.find_all('li', class_='soundList__item'):
    artist_tag = block.find('a', class_='soundTitle__username')
    title_tag = block.find('a', class_='soundTitle__title')
    if artist_tag and title_tag:
        artist = artist_tag.get_text(strip=True)
        title = title_tag.get_text(strip=True)
        tracks.append(f"{artist} - {title}")

with open('sc_parser/tracks.txt', 'w', encoding='utf-8') as file:
    for track in tracks:
        file.write(track + '\n')

print(f"Saved {len(tracks)} tracks.")

# ==== Connect to Spotify ====#
load_dotenv()

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
scope='playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope
))

user_id = sp.current_user()['id']
playlist_name = f"SoundCloud Likes {datetime.now().strftime('%Y-%m-%d')}"
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
print(f"Created playlist: {playlist['name']}")

# ==== Search and add tracks ====

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\(.*?\)|\[.*?\]', '', text)
    return text.strip()

track_uris = []
not_found=[]
with open('sc_parser/tracks.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

for line in lines:
    parts = line.split(' - ')
    if len(parts) >= 2:
        artist = clean_text(parts[-2])
        title = clean_text(parts[-1])
    else:
        print(f"⚠️ Skipped: '{line}' — not enough parts")
        continue

    query = f"track:{title} artist:{artist}"
    results = sp.search(q=query, type='track', limit=1)
    items = results['tracks']['items']

    if items:
        item = items[0]
        uri = item['uri']
        found_artist = item['artists'][0]['name']
        found_title = item['name']
        track_uris.append(uri)
        print(f"✔ Found: {found_artist} – {found_title}")
    else:
         not_found.append(f"{artist} - {title}")



with open('not_found_tracks.txt', 'w') as file:
    for line in not_found:
        file.write(f"{line}+\n")


# ==== Add in chunks to playlist ====#

if track_uris:
    batch_size = 100
    for i in range(0, len(track_uris), batch_size):
        batch = track_uris[i:i + batch_size]
        try:
            sp.playlist_add_items(playlist_id=playlist['id'], items=batch)
            print(f"Added: {i + len(batch)} / {len(track_uris)}")
        except spotipy.SpotifyException as e:
            print(f"❌ Failed to add batch at {i}: {e}")
    print("✅ All available tracks added.")
else:
    print("⚠️ No tracks to add.")
try:
    # os.remove('soundclound_script/html_res.html')
    os.remove('soundclound_script/tracks.txt')
    print("file deleted .")
except FileNotFoundError as ferorr:
    print(f"file wasn`t found.{ferorr.filename}")
except Exception as e:
    print(f"Error: {e}")
