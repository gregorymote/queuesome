import logging
from io import BytesIO
from urllib.parse import urlsplit

import requests
from numpy import asarray
from PIL import Image, UnidentifiedImageError

from party.models import Songs
from utils.spotify_background_color import SpotifyBackgroundColor


logger = logging.getLogger(__name__)

SPOTIFY_IMAGE_HOSTS = frozenset({'i.scdn.co', 'mosaic.scdn.co'})
IMAGE_DOWNLOAD_TIMEOUT = (3.05, 10)
MAX_IMAGE_DOWNLOAD_BYTES = 8 * 1024 * 1024
MAX_IMAGE_DIMENSION = 4096
MAX_IMAGE_PIXELS = 16_000_000
ALLOWED_IMAGE_FORMATS = frozenset({'JPEG', 'PNG', 'WEBP'})


class RemoteImageError(ValueError):
    pass


def download_spotify_image(image_url):
    try:
        parsed = urlsplit(image_url or '')
        port = parsed.port
    except ValueError as exc:
        raise RemoteImageError('Artwork URL is invalid.') from exc
    if (
        parsed.scheme != 'https'
        or parsed.username
        or parsed.password
        or port
        or parsed.hostname not in SPOTIFY_IMAGE_HOSTS
    ):
        raise RemoteImageError('Artwork must use an approved Spotify HTTPS host.')

    try:
        response = requests.get(
            image_url,
            stream=True,
            timeout=IMAGE_DOWNLOAD_TIMEOUT,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        raise RemoteImageError('Artwork download failed.') from exc

    try:
        if response.status_code != 200:
            raise RemoteImageError('Artwork download returned an invalid status.')

        content_type = response.headers.get('Content-Type', '').split(';', 1)[0]
        if content_type not in {'image/jpeg', 'image/png', 'image/webp'}:
            raise RemoteImageError('Artwork response is not a supported image.')

        try:
            content_length = int(response.headers.get('Content-Length', '0'))
        except ValueError as exc:
            raise RemoteImageError('Artwork response has an invalid size.') from exc
        if content_length > MAX_IMAGE_DOWNLOAD_BYTES:
            raise RemoteImageError('Artwork response is too large.')

        image_bytes = BytesIO()
        total_bytes = 0
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            total_bytes += len(chunk)
            if total_bytes > MAX_IMAGE_DOWNLOAD_BYTES:
                raise RemoteImageError('Artwork response is too large.')
            image_bytes.write(chunk)
    except requests.RequestException as exc:
        raise RemoteImageError('Artwork download failed.') from exc
    finally:
        response.close()

    image_bytes.seek(0)
    try:
        with Image.open(image_bytes) as image:
            if image.format not in ALLOWED_IMAGE_FORMATS:
                raise RemoteImageError('Artwork has an unsupported image format.')
            width, height = image.size
            if (
                width > MAX_IMAGE_DIMENSION
                or height > MAX_IMAGE_DIMENSION
                or width * height > MAX_IMAGE_PIXELS
            ):
                raise RemoteImageError('Artwork dimensions are too large.')
            image.load()
            return image.copy()
    except (UnidentifiedImageError, OSError) as exc:
        raise RemoteImageError('Artwork response is not a valid image.') from exc


def _background_color(image, fallback='130, 128, 131'):
    try:
        colors = SpotifyBackgroundColor(img=asarray(image.convert('RGB'))).best_color()
        intensity = colors[0] * 0.299 + colors[1] * 0.587 + colors[2] * 0.114
        if intensity < 186:
            return ', '.join(str(round(channel)) for channel in colors)
    except Exception:
        logger.exception('Unable to determine artwork background color.')
    return fallback


def get_bg_color(song_id):
    song = Songs.objects.get(id=song_id)
    try:
        image = download_spotify_image(song.art)
    except RemoteImageError:
        logger.exception('Unable to download artwork for song %s.', song_id)
        return

    song.color = _background_color(image)
    song.save(update_fields=['color'])


def get_album_color(image_url):
    try:
        image = download_spotify_image(image_url)
    except RemoteImageError:
        logger.exception('Unable to download album artwork.')
        return '130, 128, 131'
    return _background_color(image)
