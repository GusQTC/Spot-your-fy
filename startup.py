from flask_spotify_auth import getAuth, refreshAuth, getToken

# Add your client ID
CLIENT_ID = "0b47403475bd4b2c9272a2ce9557f884"

# aDD YOUR CLIENT SECRET FROM SPOTIFY
CLIENT_SECRET = "d382038545e8484f93bf7d70dd97772c"

# Port and callback url can be changed or ledt to localhost:5000
PORT = "5000"
CALLBACK_URL = "http://localhost:5000/callback/"

# Add needed scope from spotify user
SCOPE = "user-read-private"
# token_data will hold authentication header with access code, the allowed scopes, and the refresh countdown
TOKEN_DATA = []


def getUser():
    return f"https://accounts.spotify.com/authorize/?client_id={CLIENT_ID}&response_type=code&redirect_uri={CALLBACK_URL}&scope={SCOPE}"


def getUserToken(code):
    global TOKEN_DATA
    TOKEN_DATA = getToken(
        code, CLIENT_ID, CLIENT_SECRET, "http://localhost:5000/callback/"
    )


def refreshToken(time):
    time.sleep(time)
    TOKEN_DATA = refreshAuth()


def getAccessToken():
    return TOKEN_DATA
