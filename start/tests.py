from unittest.mock import patch

from django.test import TestCase
from django.urls import resolve

from utils.util_auth import OAUTH_STATE_SESSION_KEY


class PublicStartPageTests(TestCase):
    def test_root_uses_start_view(self):
        match = resolve('/')

        self.assertEqual(match.view_name, 'start')

    def test_start_page_renders(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'start.html')

    @patch(
        'start.views.generate_url',
        return_value='https://accounts.spotify.test/authorize',
    )
    def test_starting_oauth_stores_and_sends_session_state(self, generate_url):
        response = self.client.post('/index', {'blank': ''})

        self.assertRedirects(
            response,
            'https://accounts.spotify.test/authorize',
            fetch_redirect_response=False,
        )
        state = self.client.session[OAUTH_STATE_SESSION_KEY]
        self.assertGreaterEqual(len(state), 32)
        self.assertEqual(generate_url.call_args.kwargs['state'], state)
