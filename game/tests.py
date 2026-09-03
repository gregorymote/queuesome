from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from party.models import Category, Library, Party, Searches, Songs, Users


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


class CategoryTransitionTests(TestCase):
    def setUp(self):
        self.party = Party.objects.create(
            name='Category party',
            state='choose_category',
            lib_repo=set(),
            indices=set(),
        )
        self.client = Client()
        session = self.client.session
        session.save()
        self.leader = Users.objects.create(
            name='Leader',
            party=self.party,
            sessionID=session.session_key,
            turn='picking',
        )
        self.member = Users.objects.create(
            name='Member', party=self.party, turn='not_picked'
        )

    def offer_library(self, name='Rock'):
        library = Library.objects.create(name=name, visible=True)
        self.party.lib_repo = {str(library.pk)}
        self.party.indices = {'0'}
        self.party.save()
        return library

    def test_leader_category_selection_is_idempotent(self):
        library = self.offer_library()
        data = {
            'result': str(library.pk),
            'artist': '',
            'custom': '',
            'custom_desc': '',
        }

        first = self.client.post(
            reverse('pick_category', kwargs={'pid': self.party.pk}), data
        )
        replay = self.client.post(
            reverse('pick_category', kwargs={'pid': self.party.pk}), data
        )

        self.assertEqual(first.status_code, 302)
        self.assertEqual(replay.status_code, 302)
        self.party.refresh_from_db()
        self.leader.refresh_from_db()
        self.assertEqual(self.party.state, 'pick_song')
        self.assertEqual(self.party.roundTotal, 1)
        self.assertEqual(self.leader.turn, 'has_picked')
        self.assertEqual(
            Category.objects.filter(party=self.party, roundNum=1).count(), 1
        )

    def test_unoffered_library_is_rejected(self):
        self.offer_library('Offered')
        unoffered = Library.objects.create(name='Unoffered', visible=True)

        response = self.client.post(
            reverse('pick_category', kwargs={'pid': self.party.pk}),
            {
                'result': str(unoffered.pk),
                'artist': '',
                'custom': '',
                'custom_desc': '',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.party.refresh_from_db()
        self.assertEqual(self.party.state, 'choose_category')
        self.assertEqual(self.party.roundTotal, 0)
        self.assertFalse(Category.objects.filter(party=self.party).exists())

    def test_non_leader_cannot_select_offered_category(self):
        library = self.offer_library()
        member_client = Client()
        session = member_client.session
        session.save()
        self.member.sessionID = session.session_key
        self.member.save(update_fields=['sessionID'])

        response = member_client.post(
            reverse('pick_category', kwargs={'pid': self.party.pk}),
            {
                'result': str(library.pk),
                'artist': '',
                'custom': '',
                'custom_desc': '',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.party.refresh_from_db()
        self.assertEqual(self.party.state, 'choose_category')
        self.assertFalse(Category.objects.filter(party=self.party).exists())

    def test_legacy_picker_uses_same_transition_rules(self):
        library = self.offer_library()

        response = self.client.post(
            reverse('choose_category', kwargs={'pid': self.party.pk}),
            {
                'cat_choice': str(library.pk),
                'artist': '',
                'custom': '',
                'custom_desc': '',
                'scatt_radio': 'Song',
                'search': '',
                'result': '-1',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.party.refresh_from_db()
        self.assertEqual(self.party.state, 'pick_song')
        self.assertEqual(self.party.roundTotal, 1)
