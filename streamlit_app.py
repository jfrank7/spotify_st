import streamlit as st
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd


def get_spotify():
    """
    Extract and transform spotify data into a dataframe with top 50 songs
    Output: Dataframe
    """
    
    # Change environment variables
    cid = '350a1fdf522145b6b70a780c4f1f3233'
    secret = 'e691637d43c04683897fec63a069d797'

    # Create a Spotipy client
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id = cid,
        client_secret = secret,
        redirect_uri = 'http://localhost:7777/callback',
        scope = 'user-top-read'
        ))

    # Get the user's top 50 tracks
    results = sp.current_user_top_tracks(
        limit = 50,
        offset = 0,
        time_range = 'short_term' # short_term = 4 weeks, medium_term = 6 months
        )
        
    return results

def transform_spotify(spotify_data):
    # Process the list of top tracks
    list_of_artist_names = []
    list_of_song_names = []
    list_of_albums = []

    for result in spotify_data['items']:
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

st.write('''This app uses the Streamlit platform as a user friendly way to interact with.
         
It interacts with Spotify's API to access live data on the user and display it in a simple table.

All three steps of the ETL process are followed to reach the end result.

Data cleaning had to be applied to the artists variable to account for songs with multiple artists. For simplicity the main artist according to spotify was used and displayed.
''')

# Display section header
st.subheader('Your Spotify Top 10s')

# Streamlit button 1
if st.button("Run Spotify Analysis (LOGIN REQUIRED)"):
    # Extract and transform Spotify data
    all_songs = transform_spotify(get_spotify())

    # Display the charts side by side
    col1, col2 = st.columns(2)
    
    # Display the top 10 songs
    with col1:
        st.write('**Top 10 Songs**')
        st.dataframe(top10_songs(all_songs))

    # Display the top 10 artists
    with col2:
        st.write('**Top 10 Artists**')
        st.dataframe(top10_artists(all_songs))
    
# Streamlit button 2
if st.button("Show example"):
    # Extract and transform Spotify data
    
    # Open the JSON file for reading
    with open('example.json', 'r') as json_file:
        # Load the JSON data into the dictionary
        data = json.load(json_file)
    all_songs = transform_spotify(data)

    # Display the charts side by side
    col1, col2 = st.columns(2)
    
    # Display the top 10 songs
    with col1:
        st.write('**Top 10 Songs**')
        st.dataframe(top10_songs(all_songs))

    # Display the top 10 artists
    with col2:
        st.write('**Top 10 Artists**')
        st.dataframe(top10_artists(all_songs))