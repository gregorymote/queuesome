from django.test import SimpleTestCase
from django.urls import resolve


class PublicStartPageTests(SimpleTestCase):
    def test_root_uses_start_view(self):
        match = resolve('/')

        self.assertEqual(match.view_name, 'start')

    def test_start_page_renders(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'start.html')
