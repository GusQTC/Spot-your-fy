"""This runs the main flask application"""
import configparser
import secrets

import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, redirect, render_template, flash
import bleach
from schema import Schema, And

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

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
                        redirect_uri="https://spot-your-fy.uc.r.appspot.com/",
                        scope=['playlist-read-private'])
sp_user_playlists = spotipy.Spotify(auth_manager=sp_auth)


@app.route('/')
def index():
    """Makes the index template"""
    return render_template("index.html")


def get_recommendations(track_ex, artist_ex):
    """Gets recommendations based on user input"""
    schema = Schema(And(str, len))

    if track_ex and artist_ex:
        artist_ex = schema.validate(bleach.clean(artist_ex))
        track_ex = schema.validate(bleach.clean(track_ex))

    elif artist_ex and not track_ex:
        artist_ex = schema.validate(bleach.clean(artist_ex))

    elif not artist_ex and track_ex:
        track_ex = schema.validate(bleach.clean(track_ex))

    else:
        flash('Please enter a valid track and artist name.')
        return redirect(url_for('index'))

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
        song_links.append((song_name, song_link, song_art))
    return render_template('recs.html', result=song_links)


def check_albums(artist):
    """Checks albums of a given artist"""
    schema = Schema(And(str, len))
    while not artist:
        flash('Please enter a valid artist name.')
        return redirect(url_for('index'))
    artist = schema.validate(artist)
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
    return render_template('albums.html',
                        result=album_names, followers=followers, artist_name=artist_name)


@app.route('/', methods=['GET', 'POST'])
def buttons():
    """Makes the buttons and renders templates accordingly"""
    if request.form.get('get_recs') == 'Get Recommendations':
        track_ex = request.form['track_ex']
        artist_ex = request.form['art_ex']
        return get_recommendations(track_ex, artist_ex)

    if request.form.get('get_albums') == 'Check Albums!':
        artist = request.form['artist']
        return check_albums(artist)

    flash('Please enter a valid input.')
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run()
