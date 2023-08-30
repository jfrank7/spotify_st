import streamlit as st
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util
import pandas as pd
import socket


def get_spotify(submitted, client_id_input, client_secret_input):
    """
    Extract and transform spotify data into a dataframe with top 50 songs
    Output: Dataframe
    """
    
    # Change environment variables
    cid = '350a1fdf522145b6b70a780c4f1f3233'
    secret = 'e691637d43c04683897fec63a069d797'
    
    if submitted:
        # Set environment variables with the provided credentials
        cid = client_id_input
        secret = client_secret_input

    # Create a Spotipy client

    # Attempt to close the socket if it's already open
    try:
        existing_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        existing_socket.connect(('localhost', 7777))
        existing_socket.close()
    except ConnectionRefusedError:
        # The connection was refused, meaning the socket wasn't open.
        print("No existing socket found on localhost:7777.")
    except Exception as e:
        print(f"An error occurred while closing the socket: {e}")

    # sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    #     client_id = cid,
    #     client_secret = secret,
    #     redirect_uri = 'http://localhost:7777/callback',
    #     scope = 'user-top-read'
    #     ))
    
    token = util.prompt_for_user_token(
        client_id = cid,
        client_secret = secret,
        redirect_uri = 'http://localhost:7777/callback',
        scope = 'user-top-read'
        )
    sp = spotipy.Spotify(auth=token)
    
    # Get the user's top 50 tracks
    results = sp.current_user_top_tracks(
        limit = 50,
        offset = 0,
        time_range = 'short_term' # short_term = 4 weeks, medium_term = 6 months
        )

    # Process the list of top tracks
    list_of_artist_names = []
    list_of_song_names = []
    list_of_albums = []

    for result in results['items']:
        list_of_artist_names.append(result["artists"][0]["name"])
        list_of_song_names.append(result["name"])
        list_of_albums.append(result["album"]["name"])

    # Create a DataFrame to store the processed data
    all_songs = pd.DataFrame(
        {
            'Artist': list_of_artist_names,
            'Song': list_of_song_names,
            'Album': list_of_albums,
        })
    
    return all_songs

def top10_songs(songs):
    """ 
    Select the top 10 songs and format the DataFrame
    Output: Dataframe
    """
    top10_songs = songs.head(10)
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

Finally, open the app and click on "Settings" at the top right of the screen and you will find your credentials.

**Disclaimer:**
These credentials are used to access your accounts data, not the account itself. They cannot be used to modify your account in any way. The credentials are not saved anywhere, they are used temporarily to access your data locally.
        ''')

# Display input request to get credentials
with st.form("my_form"):
    st.subheader('Credentials')

    # Input fields for Client ID and Client Secret
    client_id_input = st.text_input('**Client ID**', placeholder='Insert CID...')
    client_secret_input = st.text_input('**Client Secret**', placeholder='Insert secret...')
    submitted = st.form_submit_button("Submit")

# Extract and transform spotify data
all_songs = get_spotify(submitted, client_id_input, client_secret_input)

# Display section header
st.subheader('Your Spotify Top 10s')

if not submitted:
    st.write('This is an example...')

# Display the top 10 songs
st.write('**Top 10 Songs**')
st.dataframe(top10_songs(all_songs))

# Display the top 10 artists
st.write('**Top 10 Artists**')
st.dataframe(top10_artists(all_songs))

