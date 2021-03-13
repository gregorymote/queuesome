from party.models import Party, Users, Devices
from utils.util_auth import check_token
import spotipy

def activate_device(token_info, party_id, scope=None, client_id = None,
        client_secret = None, redirect_uri = None):
    p = Party.objects.get(pk = party_id)
    token = check_token(
                token_info=p.token_info,
                party_id=party_id,
                scope=scope,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri
    )
    spotify_object = spotipy.Spotify(auth=token)
    device_results = spotify_object.devices()
    device_results = device_results['devices']
    flag = True
    for device in device_results:
        if device["id"] == p.deviceID:
            if not device["is_active"]:
                spotify_object.transfer_playback(
                    device_id=p.deviceID,
                    force_play=False
                )
            else:
                flag = False
    if flag:
        p.debug = p.debug + " **!!!** Device Not Found"
        p.save()


def is_device_active(token_info, party_id, scope=None, client_id = None,
        client_secret = None, redirect_uri = None):
    p = Party.objects.get(pk=party_id)
    token = check_token(
                token_info=p.token_info,
                party_id=party_id,
                scope=scope,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri
    )
    spotify_object = spotipy.Spotify(auth=token)
    device_results = spotify_object.devices()
    device_results = device_results['devices']
    for device in device_results:
        if device["id"] == p.deviceID:
            return(True)
    return False