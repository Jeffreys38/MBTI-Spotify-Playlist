import streamlit as st
import json, validators, spotipy, re
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import requests

SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

# SPOTIFY API
auth_response = requests.post(
    'https://accounts.spotify.com/api/token',
    data={'grant_type': 'client_credentials'},
    auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
)

access_token = auth_response.json().get('access_token')
sp = spotipy.Spotify(auth=access_token)

# GET PLAYLIST ID BY URL
@st.cache_data
def extract_playlist_id(url):
    match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
    return match.group(1) if match else None

# GET PLAYLIST INFO
@st.cache_data
def playlist_info(playlist):
    track_ids = [item['track']['id'] for item in playlist['tracks']['items'] if item['track'] and item['track']['id']]

    # split into 100 songs for each
    chunks = [track_ids[i:i+100] for i in range(0, len(track_ids), 100)]

    all_features = []
    for chunk in chunks:
        try:
            features = sp.audio_features(chunk)
            if features:
                all_features.extend([f for f in features if f])  # remove none 
        except Exception as err:
            st.warning("Có lỗi xảy ra, vui lòng thử lại!")
            print(err)
            continue

    if not all_features:
        return None

    n = len(all_features)

    return {    
        "danceability": sum(f["danceability"] for f in all_features) / n,
        "energy": sum(f["energy"] for f in all_features) / n,
        "tempo": sum(f["tempo"] for f in all_features) / n,
        "valence": sum(f["valence"] for f in all_features) / n,
        "acousticness": sum(f["acousticness"] for f in all_features) / n,
        "instrumentalness": sum(f["instrumentalness"] for f in all_features) / n
    }


# UI
playlist_url = st.text_input("Dán link playlist Spotify vào đây", placeholder = "https://open.spotify.com/playlist/4SyqPrpD1yGm33Ychi3ac0?si=b3b9d2e173c646ed")

if playlist_url:
    if validators.url(playlist_url):
        playlist_id = extract_playlist_id(playlist_url)
        playlist = sp.playlist(playlist_id)
        
        st.write(playlist["name"])
        st.image(playlist["images"][0]["url"], caption="Playlist của bạn")
        
        # show playlist info
        print(playlist_info(playlist))
    else:
        st.warning("URL không hợp lệ hoặc không thể tìm thấy")
else:
    st.warning("Bạn cần nhập URL trước khi xem kết quả")