import pandas as pd
import sqlalchemy as db
import requests
from spotify_genres import genres  # List of genres from Spotify
from api_key import *  # Imports get_spotify_api_key function
import sys  # Import sys module for exiting on error


engine = db.create_engine('sqlite:///music_info.db')  # Create SQLite database engine


def create_db(query_words):
    """
    Fetches songs from Spotify API based on genres and query words, stores them in SQLite database tables.

    Args:
    - query_words (str): Keywords used to refine Spotify API search.

    Returns:
    - None
    """
    SPOTIFY_API_KEY = get_spotify_api_key()
    headers = {"Authorization": "Bearer {token}".format(token=SPOTIFY_API_KEY)}

    for genre in genres:
        final_query = f"{genre} {' '.join(query_words)}"  # Construct query for Spotify API search
        # final_query = f"genre:{genre} {' '.join(query_words)}"  # Alternative query format

        params = {
            "q": final_query,
            "type": "track",
            "limit": 5
        }

        response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
        data = response.json()

        if "error" in data:
            # Handle API error response
            print(f"Error from Spotify API: {data['error']['message']}")
            sys.exit(0)

        songs_dict = {}

        for i, item in enumerate(data['tracks']['items']):
            # Extract song details from API response
            song_name = item['name']
            artist_name = item['artists'][0]['name']
            album_name = item['album']['name']
            song_link = item['external_urls']['spotify']
            songs_dict[i + 1] = {
                "song_name": song_name,
                "artist_name": artist_name,
                "album_name": album_name,
                "song_link": song_link
            }

        dict_to_table(songs_dict, genre.replace("-", ""))  # Store songs in SQLite table


def dict_to_table(genre_dict, genre):
    """
    Converts a dictionary of songs into a pandas DataFrame and stores it as a table in the SQLite database.

    Args:
    - genre_dict (dict): Dictionary containing song information.
    - genre (str): Genre name used as the table name.

    Returns:
    - None
    """
    df = pd.DataFrame.from_dict(genre_dict, orient='index')
    df.to_sql(genre, con=engine, if_exists='replace')  # Store DataFrame as SQLite table
