import json

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models

ENCRYPTED_PREFIX = 'fernet:'


def get_token_cipher():
    try:
        return MultiFernet([
            Fernet(key) for key in settings.SPOTIFY_TOKEN_ENCRYPTION_KEYS
        ])
    except (TypeError, ValueError) as exc:
        raise ImproperlyConfigured(
            'SPOTIFY_TOKEN_ENCRYPTION_KEYS must contain valid Fernet keys.'
        ) from exc


def encrypt_token_payload(value):
    if value in (None, ''):
        return value
    if not isinstance(value, str):
        value = json.dumps(value, separators=(',', ':'), sort_keys=True)
    if value.startswith(ENCRYPTED_PREFIX):
        return value
    encrypted = get_token_cipher().encrypt(value.encode()).decode()
    return ENCRYPTED_PREFIX + encrypted


def decrypt_token_payload(value):
    if value in (None, '') or not value.startswith(ENCRYPTED_PREFIX):
        return value
    try:
        return get_token_cipher().decrypt(
            value.removeprefix(ENCRYPTED_PREFIX).encode()
        ).decode()
    except InvalidToken as exc:
        raise ValueError('Stored Spotify token could not be decrypted.') from exc


class EncryptedTokenField(models.TextField):
    description = 'Authenticated encrypted Spotify token payload'

    def from_db_value(self, value, expression, connection):
        return decrypt_token_payload(value)

    def to_python(self, value):
        return decrypt_token_payload(value)

    def get_prep_value(self, value):
        return encrypt_token_payload(value)
