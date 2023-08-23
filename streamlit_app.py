import streamlit as st
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

st.header('Spotify Top 10s')

st.subheader('Description')

st.write('''Log in here to obtain your Client ID and Client Secret: https://developer.spotify.com/dashboard/login

Then click on your username at the top right, then on "dashboards".

There create an app. Add any name and description, and copy this for the **Redirect URI:** http://localhost:7777/callback

Finally, open the app and you will find your credentials.

**Disclaimer:**
These credentials are used to access your accounts data, not the account itself. They cannot be used to modify your account in any way. The credentials are not saved anywhere, they are used temporarily to access your data.
         ''')

os.environ['SPOTIPY_CLIENT_ID'] = '350a1fdf522145b6b70a780c4f1f3233'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'e691637d43c04683897fec63a069d797'
example = True

with st.form("my_form"):
    st.subheader('Credentials')

    cid = st.text_input('**Client ID**', placeholder='Insert CID...')
    secret = st.text_input('**Client Secret**', placeholder='Insert secret...')
    
    ### Here a stopper should be that only runs the next fancy code after it gets both inputs
    
    submitted = st.form_submit_button("Submit")
    if submitted:

        ### Here is the fancy code that does everything
        
        os.environ['SPOTIPY_CLIENT_ID'] = cid
        os.environ['SPOTIPY_CLIENT_SECRET'] = secret

st.subheader('Your Spotify Top 10s')

os.environ['SPOTIPY_REDIRECT_URI'] ='http://localhost:7777/callback'

username = ""
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret) 
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
scope = 'user-top-read'
token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_top_tracks(limit=50,offset=0,time_range = 'short_term') # short_term = 4 weeks, medium_term = 6 months
    for song in range(50):
        list = []
        list.append(results)
        with open('top50_data.json', 'w', encoding='utf-8') as f:
            json.dump(list, f, ensure_ascii=False, indent=4)
else:
    print("Can't get token for", username)

with open('top50_data.json') as f:
    data = json.load(f)

list_of_results = data[0]["items"]
list_of_artist_names = []
list_of_artist_uri = []
list_of_song_names = []
list_of_song_uri = []
list_of_durations_ms = []
list_of_explicit = []
list_of_albums = []
list_of_popularity = []

for result in list_of_results:
    this_artists_name = result["artists"][0]["name"]
    list_of_artist_names.append(this_artists_name)
    this_artists_uri = result["artists"][0]["uri"]
    list_of_artist_uri.append(this_artists_uri)
    list_of_songs = result["name"]
    list_of_song_names.append(list_of_songs)
    song_uri = result["uri"]
    list_of_song_uri.append(song_uri)
    list_of_duration = result["duration_ms"]
    list_of_durations_ms.append(list_of_duration)
    song_explicit = result["explicit"]
    list_of_explicit.append(song_explicit)
    this_album = result["album"]["name"]
    list_of_albums.append(this_album)
    song_popularity = result["popularity"]
    list_of_popularity.append(song_popularity)
    
all_songs = pd.DataFrame(
    {'artist': list_of_artist_names,
    'artist_uri': list_of_artist_uri,
    'song': list_of_song_names,
    'song_uri': list_of_song_uri,
    'duration_ms': list_of_durations_ms,
    'explicit': list_of_explicit,
    'album': list_of_albums,
    'popularity': list_of_popularity
    
    })

all_songs_saved = all_songs.to_csv('top50_songs.csv')

top50 = all_songs

top50 = top50[['artist', 'song', 'album']]

top50.index = top50.index + 1

if example:
    st.write('This is an example...')

st.write('**Top 10 Songs**')
# filter for date range

#code for the top 10
st.dataframe(top50.head(10))

st.write('**Top 10 Artists**')
# filter for date range

#code for the top 10
st.dataframe(top50.head(10))
