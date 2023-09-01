import configparser
import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, render_template

app = Flask(__name__)

parser = configparser.ConfigParser()
parser.read("spotify.conf")
client_id = parser.get("spotify_creds", "client_id")
client_secret = parser.get("spotify_creds", "client_secret")
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))

scope_user_top = "user-top-read"
scope_user_playlists = "playlist-read-private"

sp_oauth = oauth2.SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri='http://localhost:5000/spotify/callback',
    scope=['user-top-read']
)

sp_user_top = spotipy.Spotify(auth_manager=sp_oauth)
sp_auth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, 
                        redirect_uri="https://accounts.spotify.com",scope=scope_user_playlists)
sp_user_playlists = spotipy.Spotify(auth_manager=sp_auth)


@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/')
def index():
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect(url_for('login'))
    else:
        return render_template("index.html")

@app.route("/spotify/callback")
def spotify_callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect('/')


@app.route('/form', methods=['GET','POST'])
def my_form_post():
    token_info = session.get("token_info", None)
    # If there's no token in the session, redirect user to login
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    else:

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
    
        if request.form.get('get_followers') == 'Check Followers!':
            name = request.form['artist']
            results_artists = sp.search(q='artist:' + name, type='artist')
            items = results_artists['artists']['items']
            if len(items) > 0:
                artist = items[0]
                uri = artist['external_urls']['spotify']
                followers = artist['followers']['total']
                return render_template('followers.html', followers=followers, artist_name = name)
        
        if request.form.get('get_tracks') == 'Check Tracks!':
            results = sp_user_top.current_user_top_tracks()
            user = sp_user_top.current_user()

            tracks = results['items']
            track_names = []
            for track in tracks:
                track_names.append(track['name'])
            return render_template('top_tracks.html', track_names=track_names, user = user)
        
        if request.form.get('get_playlists') == 'Check Playlists!':
            results = sp_user_playlists.current_user_playlists()
            user = sp.current_user()

            playlists = results['items']
            playlist_names = []
            for playlist in playlists:
                playlist_names.append(playlist['name'])
            return render_template('playlists.html', playlist_names=playlist_names, user = user)

if __name__ == '__main__':
    app.run()
