import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import json
from flask import Flask
from flask import request
from flask import render_template
from flask import Blueprint

app = Flask(__name__)

parser = configparser.ConfigParser()
parser.read("spotify.conf")
client_id = parser.get("spotify_creds", "client_id")
client_secret = parser.get("spotify_creds", "client_secret")
SPOTIPY_REDIRECT_URI = "http://localhost:3000"
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))

scope_user_top = "user-top-read"
scope_user_playlists = "playlist-read-private"
sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri= SPOTIPY_REDIRECT_URI, scope=scope_user_top)
sp_user_top = spotipy.Spotify(auth_manager=sp_oauth)
sp_auth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=SPOTIPY_REDIRECT_URI,scope=scope_user_playlists)
sp_user_playlists = spotipy.Spotify(auth_manager=sp_auth)



@app.route('/')
def my_form():
    return render_template("index.html") # This should be the name of your HTML file

@app.route('/', methods=['GET','POST'])
def my_form_post():
    

    if request.form.get('get_albums') == 'Check Albums!':
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
    
    elif request.form.get('get_followers') == 'Check Followers!':
        name = request.form['artist']
        results_artists = sp.search(q='artist:' + name, type='artist')
        items = results_artists['artists']['items']
        if len(items) > 0:
            artist = items[0]
            uri = artist['external_urls']['spotify']
            followers = artist['followers']['total']
            return render_template('followers.html', followers=followers, artist_name = name)
    
    elif request.form.get('get_tracks') == 'Check Tracks!':
        results = sp_user_top.current_user_top_tracks()
        user = sp_user_top.current_user()

        tracks = results['items']
        track_names = []
        for track in tracks:
            track_names.append(track['name'])
        return render_template('top_tracks.html', track_names=track_names, user = user)
    
    elif request.form.get('get_playlists') == 'Check Playlists!':
        results = sp_user_playlists.current_user_playlists()
        user = sp.current_user()

        playlists = results['items']
        playlist_names = []
        for playlist in playlists:
            playlist_names.append(playlist['name'])
        return render_template('playlists.html', playlist_names=playlist_names, user = user)

if __name__ == '__main__':
    app.run(debug=True)


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

