import streamlit as st
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import pandas as pd


def get_spotify(submitted, client_id_input, client_secret_input):
    """
    Extract and transform spotify data into a dataframe with top 50 songs
    Output: Dataframe
    """
    
    # Change environment variables
    if submitted:
        # Set environment variables with the provided credentials
        os.environ['SPOTIPY_CLIENT_ID'] = client_id_input
        os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret_input
        example = False # Example flag
        
    else:
        # Set Spotify Client ID and Client Secret example
        os.environ['SPOTIPY_CLIENT_ID'] = '350a1fdf522145b6b70a780c4f1f3233'
        os.environ['SPOTIPY_CLIENT_SECRET'] = 'e691637d43c04683897fec63a069d797'
        example = True # Example flag

    username = ""
    os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:7777/callback'
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id_input, client_secret=client_secret_input)

    # Get a Spotify object
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    scope = 'user-top-read'
    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        # Get the user's top 50 tracks
        results = sp.current_user_top_tracks(limit=50,offset=0,time_range = 'short_term') # short_term = 4 weeks, medium_term = 6 months
        
        # Save the top 50 tracks to a JSON file
        for song in range(50):
            list = []
            list.append(results)
            with open('top50_data.json', 'w', encoding='utf-8') as f:
                json.dump(list, f, ensure_ascii=False, indent=4)
    else:
        print("Can't get token for", username)

    # Load the saved data from the JSON file
    with open('top50_data.json') as f:
        data = json.load(f)

    # Extract relevant information from the loaded data
    list_of_results = data[0]["items"]

    # Process the list of top tracks
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

    # Create a DataFrame to store the processed data
    all_songs = pd.DataFrame(
        {
            'Artist': list_of_artist_names,
            'Artist_uri': list_of_artist_uri,
            'Song': list_of_song_names,
            'Song_uri': list_of_song_uri,
            'duration_ms': list_of_durations_ms,
            'Explicit': list_of_explicit,
            'Album': list_of_albums,
            'Popularity': list_of_popularity
        })
    
    return all_songs, example

def top10_songs(songs):
    """ 
    Select the top 10 songs and format the DataFrame
    Output: Dataframe
    """
    top10_songs = songs.head(10)
    top10_songs = top10_songs[['Artist', 'Song', 'Album']]
    top10_songs.index = top10_songs.index + 1
    
    return top10_songs

def top10_artists(songs):
    """
    Select the top 10 artists and format the DataFrame.
    
    Takes in a ordered dataframe of songs data
    
    Input: Dataframe
    Output: Dataframe
    """
    top_artists = songs['Artist'].value_counts().sort_values(ascending=False)
    top10_artists = top_artists.head(10)
    top10_artists = pd.DataFrame({'Artist': top10_artists.index, 'Songs in Top 50':
    top10_artists.values})
    top10_artists.index = top10_artists.index + 1
    
    return top10_artists

############
### Main ###
############

# Display the header
st.header('Spotify Top 10s')

# Display the description
st.subheader('Description')

st.write('''Log in here to obtain your Client ID and Client Secret: https://developer.spotify.com/dashboard/login

Then click on your username at the top right, then on "dashboards".

There create an app. Add any name and description, and copy this for the **Redirect URI:** http://localhost:7777/callback

Finally, open the app and you will find your credentials.

**Disclaimer:**
These credentials are used to access your accounts data, not the account itself. They cannot be used to modify your account in any way. The credentials are not saved anywhere, they are used temporarily to access your data.
        ''')

# Display input request to get credentials
with st.form("my_form"):
    st.subheader('Credentials')

    # Input fields for Client ID and Client Secret
    client_id_input = st.text_input('**Client ID**', placeholder='Insert CID...')
    client_secret_input = st.text_input('**Client Secret**', placeholder='Insert secret...')
    submitted = st.form_submit_button("Submit")

# Extract and transform spotify data
all_songs, example = get_spotify(submitted, client_id_input, client_secret_input)

# Display section header
st.subheader('Your Spotify Top 10s')

if example:
    st.write('This is an example...')

# Display the top 10 songs
st.write('**Top 10 Songs**')
st.dataframe(top10_songs(all_songs))

# Display the top 10 artists
st.write('**Top 10 Artists**')
st.dataframe(top10_artists(all_songs))

