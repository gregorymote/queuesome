from party.models import Party, Users, Devices
from utils.util_auth import check_token
import spotipy

def activate_device(pid):
    p = Party.objects.get(pk = pid)
    token = check_token(p.token_info, pid)
    if token is None:
        token = p.token
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


def is_device_active(pid):
    p = Party.objects.get(pk = pid)
    token = check_token(p.token_info, pid)
    if token is None:
        token = p.token
    spotify_object = spotipy.Spotify(auth=token)
    device_results = spotify_object.devices()
    device_results = device_results['devices']
    for device in device_results:
        if device["id"] == p.deviceID:
            return(True)
    return False