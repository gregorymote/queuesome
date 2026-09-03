from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from party.models import Category, Party, Searches, Songs, Users


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


class RoundTransitionTests(TestCase):
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

    @patch('game.views.set_lib_repo', return_value=set())
    @patch('game.views.threading.Thread')
    def test_starting_party_is_idempotent(self, thread, set_lib_repo):
        party = Party.objects.create(name='Ready party')
        host_client, host = self.create_party_user(
            party, 'Host', is_host=True
        )

        with self.captureOnCommitCallbacks(execute=True):
            first = host_client.post(
                reverse('lobby', kwargs={'pid': party.pk}), {'blank': ''}
            )
            second = host_client.post(
                reverse('lobby', kwargs={'pid': party.pk}), {'blank': ''}
            )

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        party.refresh_from_db()
        self.assertTrue(party.started)
        self.assertEqual(Category.objects.filter(party=party).count(), 1)
        self.assertEqual(thread.call_count, 1)
        thread.return_value.start.assert_called_once_with()

    @patch('game.views.threading.Thread')
    def test_two_members_submit_one_song_each(self, thread):
        party = Party.objects.create(
            name='Picking party', state='pick_song', roundTotal=1
        )
        category = Category.objects.create(
            name='Round one', party=party, roundNum=1
        )
        first_client, first_user = self.create_party_user(party, 'First')
        second_client, second_user = self.create_party_user(party, 'Second')
        for user, uri in (
            (first_user, 'spotify:track:first'),
            (second_user, 'spotify:track:second'),
        ):
            Searches.objects.create(
                name=uri,
                uri=uri,
                art='art',
                party=party,
                user=user,
            )

        with self.captureOnCommitCallbacks(execute=True):
            first = first_client.post(
                reverse('pick_song', kwargs={'pid': party.pk}),
                {'result': 'spotify:track:first'},
            )
            second = second_client.post(
                reverse('pick_song', kwargs={'pid': party.pk}),
                {'result': 'spotify:track:second'},
            )
            replay = first_client.post(
                reverse('pick_song', kwargs={'pid': party.pk}),
                {'result': 'spotify:track:first'},
            )

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(replay.status_code, 302)
        self.assertEqual(Songs.objects.filter(category=category).count(), 2)
        self.assertEqual(
            set(Songs.objects.values_list('user_id', flat=True)),
            {first_user.pk, second_user.pk},
        )
        self.assertEqual(thread.call_count, 2)

    @patch('game.views.threading.Thread')
    def test_member_cannot_submit_another_users_search_result(self, thread):
        party = Party.objects.create(
            name='Picking party', state='pick_song', roundTotal=1
        )
        Category.objects.create(name='Round one', party=party, roundNum=1)
        client, user = self.create_party_user(party, 'Member')
        other_client, other_user = self.create_party_user(party, 'Other')
        Searches.objects.create(
            name='Other result',
            uri='spotify:track:other',
            art='art',
            party=party,
            user=other_user,
        )

        response = client.post(
            reverse('pick_song', kwargs={'pid': party.pk}),
            {'result': 'spotify:track:other'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Songs.objects.filter(user=user).exists())
        thread.assert_not_called()
