from party.models import Party, Devices
from utils.util_auth import check_token
import spotipy
from queue_it_up.settings import QDEBUG

def activate_device(party_id):
    p = Party.objects.get(pk = party_id)
    token = check_token(
                token_info=p.token_info,
                party_id=party_id,
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
    return flag


def is_device_active(party_id):
    p = Party.objects.get(pk=party_id)
    token = check_token(
                token_info=p.token_info,
                party_id=party_id,
    )
    spotify_object = spotipy.Spotify(auth=token)
    device_results = spotify_object.devices()
    device_results = device_results['devices']
    for device in device_results:
        if device["id"] == p.deviceID:
            return(True)
    return False

def get_devices(party):
    token = check_token(token_info=party.token_info, party_id=party.pk)
    spotify_object = spotipy.Spotify(auth=token)
    device_results = spotify_object.devices()
    print(device_results)
    device_results = device_results['devices']
    curr_devices = []       
    for result in device_results:
        curr_devices.append(result['id'])
        current_device = Devices.objects.filter(
            party=party, deviceID=result['id']
        ).first()
        if not current_device:
            Devices(
                name=result['name'],
                deviceID=result['id'],
                party=party
            ).save()
    all_devices = Devices.objects.filter(party=party).all()

    for device in all_devices:
        if device.deviceID not in curr_devices:
            device.delete()

def get_active_device(party):
    token = check_token(token_info=party.token_info, party_id=party.pk)
    spotify_object = spotipy.Spotify(auth=token)
    device_results = spotify_object.devices()
    devices = device_results['devices']
    print(QDEBUG, devices)
    for device in devices:
        if device['is_active']:
            return {
                'id': device['id'],
                'name': device['name'],
                'type': device['type'].lower(),
                'active': check_playback(spotify_object)
                }
    return {
        'id': None,
        'name': 'No Active Device Found',
        'type': None,
        'active': None
        }


def check_playback(spotify):
    playback = spotify.currently_playing()
    print(QDEBUG, playback)
    return playback and playback['is_playing']