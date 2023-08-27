import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
from flask import Flask
from flask import request
from flask import render_template
from flask import Blueprint

app = Flask(__name__)

parser = configparser.ConfigParser()
parser.read("Spot-your-fy/spotify.conf")
client_id = parser.get("spotify_creds", "client_id")
client_secret = parser.get("spotify_creds", "client_secret")

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))

@app.route('/')
def my_form():
    return render_template("spot.html") # This should be the name of your HTML file

@app.route('/', methods=['POST'])
def my_form_post():
    name = request.form['artist']
    results_artists = sp.search(q='artist:' + name, type='artist')
    items = results_artists['artists']['items']
    if len(items) > 0:
        artist = items[0]
        uri = artist['external_urls']['spotify']

    results = sp.artist_albums(uri, album_type='album')
    albums = results['items']
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])

    album_names = []
    for album in albums:
        album_names.append(album['name'])
    return render_template('albums.html', album_names=album_names, artist_name = name)

if __name__ == '__main__':
    app.run(debug=True)

# load the mongo_config values




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

