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
sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(client_id, client_secret)
)

sp_oauth = oauth2.SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri="https://spot-your-fy.uc.r.appspot.com/",
    scope=["user-top-read"],
)

sp_user_top = spotipy.Spotify(auth_manager=sp_oauth)
sp_auth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri="https://spot-your-fy.uc.r.appspot.com/",
    scope=["playlist-read-private"],
)
sp_user_playlists = spotipy.Spotify(auth_manager=sp_auth)


@app.route("/")
def index():
    """Makes the index template"""
    return render_template("index.html")


def search_artist(artist: str) -> dict:
    """Searches an artist on Spotify and returns a list of artist names"""
    result = sp.search(q="artist:" + artist, type="artist")
    items = result["artists"]["items"]
    return items


def search_track(track: str) -> dict:
    """Searches an artist on Spotify and returns a list of artist names"""
    result = sp.search(q="track:" + track, type="track")
    items = result["tracks"]["items"]
    return items


def sanitize_input(user_input: str) -> str:
    """Sanitizes input"""
    schema = Schema(And(str, len))
    try:
        user_input = bleach.clean(user_input)
        user_input_validated = schema.validate(user_input)
        return user_input_validated
    except ValueError:
        return None
    except TypeError:
        return None


def check_if_null(
    track: str or None, artist: str or None
) -> tuple[str or None, str or None]:
    """Checks if track or artist is null"""
    if track:
        track = sanitize_input(track)
    if artist:
        artist = sanitize_input(artist)
    return track, artist


def get_recommendations(user_track: str or None, user_artist: str or None) -> list[str]:
    """Gets recommendations based on user input"""
    uri_track = ""
    uri_artist = ""

    if user_artist != "":
        items = search_artist(user_artist)
        if len(items) > 0:
            artist = items[0]
            uri_artist = artist["external_urls"]["spotify"]

    if user_track != "":
        items = search_track(user_track)
        if len(items) > 0:
            track = items[0]
            uri_track = track["external_urls"]["spotify"]

    if uri_artist and uri_track:
        result = sp.recommendations(
            seed_artists=[uri_artist], seed_tracks=[uri_track], limit=10
        )

    elif uri_artist:
        result = sp.recommendations(seed_artists=[uri_artist], limit=10)

    elif uri_track:
        result = sp.recommendations(seed_tracks=[uri_track], limit=10)

    recommendations = result["tracks"]
    recommendations_list = []
    for track in recommendations:
        song_name = track["name"]
        song_art = track["album"]["images"][0]["url"]
        song_link = track["external_urls"]["spotify"]
        recommendations_list.append((song_name, song_link, song_art))
    return recommendations_list


def check_albums(artist: str or None) -> list[str]:
    """Checks albums of a given artist"""

    items = search_artist(artist)

    if len(items) > 0:
        artist = items[0]
        followers = artist["followers"]["total"]
        artist_name = artist["name"]
        uri = artist["external_urls"]["spotify"]

    results = sp.artist_albums(uri, album_type="album")
    albums = results["items"]
    while results["next"]:
        results = sp.next(results)
        albums.extend(results["items"])

    album_names = []
    for album in albums:
        album_name = album["name"]
        album_image_url = album["images"][0]["url"]
        album_link = album["external_urls"]["spotify"]

        album_names.append((album_name, album_link, album_image_url))
    return album_names, followers, artist_name


@app.route("/", methods=["GET", "POST"])
def buttons():
    """Makes the buttons and renders templates accordingly"""
    if request.form.get("get_recs") == "Get Recommendations":
        track_ex = request.form["track_ex"]
        artist_ex = request.form["art_ex"]
        try:
            track_ex, artist_ex = check_if_null(track_ex, artist_ex)

            if not track_ex and not artist_ex:
                flash("Please enter a valid track and artist name.")
                return redirect(url_for("index"))

            result = get_recommendations(track_ex, artist_ex)
            return render_template("recs.html", result=result)
        except TypeError as type_error:
            print(type_error)
        except ValueError as value_error:
            print(value_error)

    if request.form.get("get_albums") == "Check Albums!":
        artist = request.form["artist"]
        while not artist:
            flash("Please enter a valid artist name.")
            return redirect(url_for("index"))
        try:
            artist = sanitize_input(artist)
            album_names, followers, artist_name = check_albums(artist)
            return render_template(
                "albums.html",
                result=album_names,
                followers=followers,
                artist_name=artist_name,
            )
        except ValueError as value_error:
            print(value_error)
        except TypeError as type_error:
            print(type_error)

    flash("Please enter a valid input.")
    return redirect(url_for("index"))



app.run(use_reloader=False, passthrough_errors=True, debug=True)
