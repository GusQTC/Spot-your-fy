import configparser
import requests
import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials

# load the mongo_config values
parser = configparser.ConfigParser()
parser.read("Scripts\pipeline.conf")
client_id = parser.get("spotify_creds", "client_id")
client_secret = parser.get("spotify_creds", "client_secret")

name = input("Artist Name: ")
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))

results_artists = sp.search(q='artist:' + name, type='artist')
items = results_artists['artists']['items']
if len(items) > 0:
    artist = items[0]
    uri = artist['external_urls']['spotify']
    print(uri)

results = sp.artist_albums(uri, album_type='album')
albums = results['items']
while results['next']:
    results = sp.next(results)
    albums.extend(results['items'])

for album in albums:
    print(album['name'])

'''
AUTH_URL = 'https://accounts.spotify.com/api/token'

results = spotify.artist_albums(birdy_uri, album_type='album')
albums = results['items']
while results['next']:
    results = spotify.next(results)
    albums.extend(results['items'])

for album in albums:
    print(album['name'])
    '''

