
from __future__ import print_function
import os
import spotipy.oauth2 as oauth2
import spotipy
from ast import literal_eval
from party.models import Party


def generate_url(username=None, scope=None, client_id = None,
        client_secret = None, redirect_uri = None, cache_path = None,
        show_dialog=True):
    ''' prompts the user to login if necessary and returns
        the user token suitable for use with the spotipy.Spotify 
        constructor

        Parameters:

         - username - the Spotify username
         - scope - the desired scope of the request
         - client_id - the client id of your app
         - client_secret - the client secret of your app
         - redirect_uri - the redirect URI of your app
         - cache_path - path to location to save tokens

    '''
    
    if not client_id:
        client_id = os.getenv('SPOTIPY_CLIENT_ID')

    if not client_secret:
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

    if not redirect_uri:
        redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

    if not client_id:
        print('''
            You need to set your Spotify API credentials. You can do this by
            setting environment variables like so:

            export SPOTIPY_CLIENT_ID='your-spotify-client-id'
            export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
            export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

            Get your credentials at     
                https://developer.spotify.com/my-applications
        ''')
        raise spotipy.SpotifyException(550, -1, 'no credentials set')

    sp_oauth = oauth2.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri, 
        scope=scope,
        show_dialog=show_dialog
    )

    auth_url = sp_oauth.get_authorize_url()

    return auth_url


def get_url(path, is_cloud, ip, port):
    i = 0
    while path[i] != '/':
        i = i + 1
    start = i

    while path[i] != '\'':
        i = i + 1
    end = i
    if is_cloud:
        url = ip + path[start:end]
    else:
        url = ip + ':' + port + path[start:end]
    return url

    
def create_token(url, username=None, scope=None, client_id = None,
        client_secret = None, redirect_uri = None, cache_path = None,
        show_dialog=False):
    
    sp_oauth = oauth2.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri, 
        scope=scope,
        show_dialog=show_dialog
    )
    code = sp_oauth.parse_response_code(url)
    if code:
        token_info = sp_oauth.get_access_token(code=code, check_cache=False)
    else:
        return None
    if token_info:
        return token_info
    else:
        return None


def check_token(token_info, party_id, scope=None, client_id = None,
        client_secret = None, redirect_uri = None):
    token_info = literal_eval(token_info)
    p = Party.objects.get(pk=party_id)
    sp_oauth = oauth2.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret, 
        redirect_uri=redirect_uri,
        scope=scope
    )
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        p.token = token_info['access_token']
        p.token_info = token_info
        p.save()
    return p.token


