import configparser
import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, render_template
import datetime
import bleach, schema
from schema import Schema, And

app = Flask(__name__)

parser = configparser.ConfigParser()
parser.read("spotify.conf")
client_id = parser.get("spotify_creds", "client_id")
client_secret = parser.get("spotify_creds", "client_secret")
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))

sp_oauth = oauth2.SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri='https://spot-your-fy.uc.r.appspot.com/',
    scope=['user-top-read']
)

sp_user_top = spotipy.Spotify(auth_manager=sp_oauth)
sp_auth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, 
                        redirect_uri="https://spot-your-fy.uc.r.appspot.com/",scope=['playlist-read-private'])
sp_user_playlists = spotipy.Spotify(auth_manager=sp_auth)


@app.route('/')
def index():
        return render_template("index.html")

@app.route('/', methods=['GET', 'POST'])
def buttons():
    
    if request.form.get('get_recs') == 'Get Recommendations':
        schema = Schema(And(str, len))

        track_ex = request.form['track_ex']
        if track_ex and len(track_ex) > 0:
            track_ex = schema.validate(bleach.clean(track_ex))

        artist_ex = request.form['art_ex']
        if artist_ex and len(artist_ex) > 0:
            artist_ex = schema.validate(bleach.clean(artist_ex))


        results_artists = sp.search(q='artist:' + artist_ex, type='artist')
        items = results_artists['artists']['items']
        if len(items) > 0:
            artist = items[0]
            uri_artist = artist['external_urls']['spotify']

        results_track = sp.search(q='track:' + track_ex, type='track')
        items = results_track['tracks']['items']
        if len(items) > 0:
            track = items[0]
            uri_track = track['external_urls']['spotify']

        result = sp.recommendations(seed_artists=[uri_artist], seed_tracks=[uri_track], limit=10)
        recommendations = result['tracks']

        song_links = []
        for track in recommendations:
            song_name = track['name']
            song_art = track['album']['images'][0]['url']
            song_link = track['external_urls']['spotify']
            song_links.append((song_name, song_link))
        return render_template('recs.html', result=song_links)


    if request.form.get('get_albums') == 'Check Albums!':
        schema = Schema(And(str, len))
        artist = schema.validate(request.form['artist'])
        artist = bleach.clean(artist)
        results_artists = sp.search(q='artist:' + artist, type='artist')
        items = results_artists['artists']['items']
        if len(items) > 0:
            artist = items[0]
            followers = artist['followers']['total']
            artist_name = artist['name']
            uri = artist['external_urls']['spotify']

        results = sp.artist_albums(uri, album_type='album')
        albums = results['items']
        while results['next']:
            results = sp.next(results)
            albums.extend(results['items'])

        album_names = []
        for album in albums:
            album_name = album['name']
            album_image_url = album['images'][0]['url']
            album_link = album['external_urls']['spotify']

            album_names.append((album_name, album_link, album_image_url))
        return render_template('albums.html', result = album_names, followers = followers, artist_name = artist_name)
                        
if __name__ == '__main__':
    app.run()
