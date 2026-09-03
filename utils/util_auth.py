
from ast import literal_eval

import spotipy.oauth2 as oauth2

from party.models import Party
from queue_it_up.settings import URI, SCOPE, CLIENT_ID, CLIENT_SECRET

OAUTH_STATE_SESSION_KEY = 'spotify_oauth_state'


def generate_url(scope=SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
        redirect_uri=URI, show_dialog=True, state=None):
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
    
    sp_oauth = oauth2.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri, 
        scope=scope,
        show_dialog=show_dialog
    )

    auth_url = sp_oauth.get_authorize_url(state=state)

    return auth_url


def get_url(path, is_cloud, ip, port):
    """Build the callback URL expected by the legacy account-linking flow."""
    start = path.index('/')
    end = path.index("'", start)
    callback_path = path[start:end]
    if callback_path == '/party/auth/':
        return 'access_denied'
    if is_cloud:
        return ip + callback_path
    return ip + ':' + port + callback_path


def create_token(code=None, url=None, scope=SCOPE, client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET, redirect_uri=URI, show_dialog=False):
    sp_oauth = oauth2.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri, 
        scope=scope,
        show_dialog=show_dialog
    )
    if code is None and url is not None:
        code = sp_oauth.parse_response_code(url)
    if not code:
        return None
    return sp_oauth.get_access_token(code=code, check_cache=False)


def check_token(token_info, party_id, scope=SCOPE, client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET, redirect_uri=URI):
    token_info = literal_eval(token_info)
    party = Party.objects.get(pk=party_id)
    sp_oauth = oauth2.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret, 
        redirect_uri=redirect_uri,
        scope=scope
    )
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        party.token = token_info['access_token']
        party.token_info = token_info
        party.save()
    return party.token
