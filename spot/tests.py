import numpy as np
from unittest.mock import ANY, patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

from spot.models import Studio
from utils.spotify_background_color import SpotifyBackgroundColor
from utils.util_auth import SPOT_OAUTH_STATE_SESSION_KEY


class ImageProcessingCompatibilityTests(SimpleTestCase):
    def test_album_art_can_be_resized_with_pillow(self):
        image = np.zeros((4, 4, 3), dtype=np.uint8)

        processor = SpotifyBackgroundColor(
            image,
            image_processing_size=(2, 2),
        )

        self.assertEqual(processor.img.shape, (2, 2, 3))


class StudioSpotifyOAuthTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username='admin', email='admin@example.test', password='password'
        )
        self.client.force_login(self.admin)

    @patch(
        'spot.views.generate_url',
        return_value='https://accounts.spotify.test/authorize',
    )
    def test_login_stores_and_sends_oauth_state(self, generate_url):
        response = self.client.get('/spot/login')

        self.assertEqual(response.status_code, 302)
        state = self.client.session[SPOT_OAUTH_STATE_SESSION_KEY]
        self.assertEqual(generate_url.call_args.kwargs['state'], state)

    @patch('spot.views.create_token')
    def test_callback_rejects_invalid_state(self, create_token):
        session = self.client.session
        session[SPOT_OAUTH_STATE_SESSION_KEY] = 'expected-state'
        session.save()

        response = self.client.get(
            '/spot/auth/', {'code': 'code', 'state': 'wrong-state'}
        )

        self.assertEqual(response.status_code, 400)
        create_token.assert_not_called()
        self.assertFalse(Studio.objects.exists())

    @patch(
        'spot.views.create_token',
        return_value={
            'access_token': 'access-token',
            'refresh_token': 'refresh-token',
        },
    )
    def test_valid_callback_stores_token_for_admin(self, create_token):
        session = self.client.session
        session[SPOT_OAUTH_STATE_SESSION_KEY] = 'expected-state'
        session.save()

        response = self.client.get(
            '/spot/auth/',
            {'code': 'authorization-code', 'state': 'expected-state'},
        )

        self.assertEqual(response.status_code, 302)
        create_token.assert_called_once_with(
            code='authorization-code', redirect_uri=ANY, scope=''
        )
        studio = Studio.objects.get(admin=self.admin)
        self.assertIn('refresh-token', studio.token_info)
