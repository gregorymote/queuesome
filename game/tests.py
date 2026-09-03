from django.test import Client, TestCase
from django.urls import reverse

from party.models import Category, Party, Users


class PartyAuthorizationTests(TestCase):
    def setUp(self):
        self.party = Party.objects.create(name="Protected party")
        self.host_client, self.host = self.create_party_user(
            self.party, "Host", is_host=True
        )
        self.member_client, self.member = self.create_party_user(
            self.party, "Member"
        )

    def create_party_user(self, party, name, is_host=False):
        client = Client()
        session = client.session
        session.save()
        user = Users.objects.create(
            name=name,
            party=party,
            sessionID=session.session_key,
            isHost=is_host,
        )
        return client, user

    def test_non_member_cannot_view_lobby(self):
        response = self.client.get(reverse("lobby", kwargs={"pid": self.party.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("index"))

    def test_non_host_cannot_start_party(self):
        response = self.member_client.post(
            reverse("lobby", kwargs={"pid": self.party.pk}), {"blank": ""}
        )

        self.assertEqual(response.status_code, 403)
        self.party.refresh_from_db()
        self.assertFalse(self.party.started)
        self.assertFalse(Category.objects.filter(party=self.party).exists())

    def test_non_host_cannot_remove_party_users(self):
        response = self.member_client.post(
            reverse("users", kwargs={"pid": self.party.pk}),
            {self.host.sessionID: "", "blank": ""},
        )

        self.assertEqual(response.status_code, 403)
        self.host.refresh_from_db()
        self.assertTrue(self.host.active)

    def test_like_update_rejects_get(self):
        response = self.member_client.get(
            reverse("update_like"), {"pid": self.party.pk}
        )

        self.assertEqual(response.status_code, 405)

    def test_member_can_only_update_like_for_own_party(self):
        other_party = Party.objects.create(name="Other party")

        forbidden = self.member_client.post(
            reverse("update_like"),
            {"pid": other_party.pk, "like": "true", "action": "like_icon"},
        )
        allowed = self.member_client.post(
            reverse("update_like"),
            {"pid": self.party.pk, "like": "true", "action": "like_icon"},
        )

        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(allowed.status_code, 200)
        self.member.refresh_from_db()
        self.assertTrue(self.member.hasLiked)
        self.assertFalse(self.member.hasSkip)

    def test_party_polling_rejects_non_members(self):
        response = self.client.get(
            reverse("update_lobby"), {"pid": self.party.pk}
        )

        self.assertEqual(response.status_code, 403)
