from django.test import Client, TestCase
from django.urls import reverse

from party.models import Party, Users


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
