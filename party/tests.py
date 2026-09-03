from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from party.models import Party, Users
from utils.util_auth import OAUTH_STATE_SESSION_KEY


class HostAuthorizationTests(TestCase):
    def setUp(self):
        self.party = Party.objects.create(name="Protected party")
        self.member_client = Client()
        session = self.member_client.session
        session.save()
        Users.objects.create(
            name="Member",
            party=self.party,
            sessionID=session.session_key,
        )

    def test_non_host_cannot_poll_and_mutate_playback_device(self):
        response = self.member_client.post(
            reverse("update_set_device"), {"pid": self.party.pk}
        )

        self.assertEqual(response.status_code, 403)

    def test_device_update_rejects_get(self):
        response = self.member_client.get(
            reverse("update_set_device"), {"pid": self.party.pk}
        )

        self.assertEqual(response.status_code, 405)

    def test_non_host_cannot_inspect_spotify_devices(self):
        response = self.member_client.get(
            reverse("update_devices"), {"pid": self.party.pk}
        )

        self.assertEqual(response.status_code, 403)


class SpotifyCallbackTests(TestCase):
    def set_oauth_state(self, value='expected-state'):
        session = self.client.session
        session[OAUTH_STATE_SESSION_KEY] = value
        session.save()

    @patch('party.views.create_token')
    def test_callback_rejects_invalid_state_before_token_exchange(
        self, create_token
    ):
        self.set_oauth_state()

        response = self.client.get(
            '/party/auth/', {'code': 'code', 'state': 'wrong-state'}
        )

        self.assertEqual(response.status_code, 400)
        create_token.assert_not_called()
        self.assertFalse(Party.objects.exists())
        self.assertNotIn(OAUTH_STATE_SESSION_KEY, self.client.session)

    @patch('party.views.create_token')
    def test_callback_handles_authorization_denial_without_creating_party(
        self, create_token
    ):
        self.set_oauth_state()

        response = self.client.get(
            '/party/auth/',
            {'error': 'access_denied', 'state': 'expected-state'},
        )

        self.assertEqual(response.status_code, 302)
        create_token.assert_not_called()
        self.assertFalse(Party.objects.exists())

    @patch(
        'party.views.create_token',
        return_value={
            'access_token': 'access-token',
            'refresh_token': 'refresh-token',
            'expires_at': 1234567890,
        },
    )
    def test_valid_callback_exchanges_code_and_creates_host(self, create_token):
        self.set_oauth_state()

        response = self.client.get(
            '/party/auth/',
            {'code': 'authorization-code', 'state': 'expected-state'},
        )

        self.assertEqual(response.status_code, 302)
        create_token.assert_called_once_with(code='authorization-code')
        party = Party.objects.get()
        host = Users.objects.get(party=party)
        self.assertEqual(party.token, 'access-token')
        self.assertTrue(host.isHost)
        self.assertEqual(host.sessionID, self.client.session.session_key)

        replay = self.client.get(
            '/party/auth/',
            {'code': 'authorization-code', 'state': 'expected-state'},
        )
        self.assertEqual(replay.status_code, 400)
        self.assertEqual(Party.objects.count(), 1)
