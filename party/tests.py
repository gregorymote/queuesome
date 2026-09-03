from unittest.mock import patch

from django.db import IntegrityError, transaction
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


class PartyJoiningTests(TestCase):
    def setUp(self):
        self.party = Party.objects.create(
            name='Joinable party', joinCode='BCDF'
        )
        Users.objects.create(name='Host', party=self.party, isHost=True)

    def test_two_browser_sessions_can_join_the_same_party(self):
        first_client = Client()
        second_client = Client()

        first_response = first_client.post(
            reverse('join_party'),
            {'party_code': 'bcdf', 'user_name': 'First guest'},
        )
        second_response = second_client.post(
            reverse('join_party'),
            {'party_code': 'BCDF', 'user_name': 'Second guest'},
        )

        self.assertRedirects(
            first_response,
            reverse('lobby', kwargs={'pid': self.party.pk}),
            fetch_redirect_response=False,
        )
        self.assertRedirects(
            second_response,
            reverse('lobby', kwargs={'pid': self.party.pk}),
            fetch_redirect_response=False,
        )
        guests = Users.objects.filter(party=self.party, isHost=False)
        self.assertEqual(guests.count(), 2)
        self.assertEqual(
            {guest.name for guest in guests},
            {'First guest', 'Second guest'},
        )
        self.assertEqual(
            Users.objects.get(party=self.party, isHost=True).name,
            'Host',
        )

    def test_rejoining_from_same_session_updates_existing_membership(self):
        first_response = self.client.post(
            reverse('join_party'),
            {'party_code': 'BCDF', 'user_name': 'First name'},
        )
        second_response = self.client.post(
            reverse('join_party'),
            {'party_code': 'BCDF', 'user_name': 'Updated name'},
        )

        self.assertEqual(first_response.status_code, 302)
        self.assertEqual(second_response.status_code, 302)
        guests = Users.objects.filter(party=self.party, isHost=False)
        self.assertEqual(guests.count(), 1)
        self.assertEqual(guests.get().name, 'Updated name')

    def test_inactive_party_code_is_rejected(self):
        self.party.active = False
        self.party.save()

        response = self.client.post(
            reverse('join_party'),
            {'party_code': 'BCDF', 'user_name': 'Guest'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "we couldn't find a party with that code")
        self.assertFalse(
            Users.objects.filter(party=self.party, isHost=False).exists()
        )

    def test_validate_code_handles_missing_code(self):
        response = self.client.get(reverse('validate_code'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'valid': False})

    def test_database_rejects_duplicate_active_membership(self):
        session = self.client.session
        session.save()
        Users.objects.create(
            name='First', party=self.party, sessionID=session.session_key
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Users.objects.create(
                name='Duplicate',
                party=self.party,
                sessionID=session.session_key,
            )


class PartyNamingTests(TestCase):
    @patch('party.views.get_active_device', return_value={'id': 'device'})
    @patch('party.views.get_code', side_effect=['BCDF', 'GHJK'])
    def test_join_code_collision_is_retried(self, get_code, get_active_device):
        Party.objects.create(name='Existing', joinCode='BCDF')
        party = Party.objects.create(name='Pending')
        session = self.client.session
        session.save()
        Users.objects.create(
            name='Host',
            party=party,
            sessionID=session.session_key,
            isHost=True,
        )

        response = self.client.post(
            reverse('start_party', kwargs={'pid': party.pk}),
            {'party_name': 'Named party', 'user_name': 'Named host'},
        )

        self.assertEqual(response.status_code, 302)
        party.refresh_from_db()
        self.assertEqual(party.joinCode, 'GHJK')
        self.assertEqual(get_code.call_count, 2)

    @patch('party.views.get_active_device', return_value={'id': 'device'})
    @patch('party.views.get_code', return_value='BCDF')
    def test_join_code_retries_are_bounded(self, get_code, get_active_device):
        Party.objects.create(name='Existing', joinCode='BCDF')
        party = Party.objects.create(name='Pending')
        session = self.client.session
        session.save()
        Users.objects.create(
            name='Host',
            party=party,
            sessionID=session.session_key,
            isHost=True,
        )

        with self.assertRaises(IntegrityError):
            self.client.post(
                reverse('start_party', kwargs={'pid': party.pk}),
                {'party_name': 'Named party', 'user_name': 'Named host'},
            )

        self.assertEqual(get_code.call_count, 10)
