from unittest.mock import patch

from django.db import OperationalError
from django.test import TestCase


class HealthEndpointTests(TestCase):
    def test_liveness_does_not_require_database_query(self):
        with patch('queue_it_up.views.connection.cursor') as cursor:
            response = self.client.get('/health/live')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        self.assertEqual(response['Cache-Control'], 'no-store')
        cursor.assert_not_called()

    def test_readiness_checks_database(self):
        response = self.client.get('/health/ready')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok', 'database': 'ok'})
        self.assertEqual(response['Cache-Control'], 'no-store')

    @patch(
        'queue_it_up.views.connection.cursor',
        side_effect=OperationalError('database unavailable'),
    )
    def test_readiness_returns_503_when_database_is_unavailable(self, cursor):
        response = self.client.get('/health/ready')

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {'status': 'unavailable', 'database': 'unavailable'},
        )
        self.assertEqual(response['Cache-Control'], 'no-store')
        cursor.assert_called_once_with()

    def test_health_endpoints_reject_post(self):
        self.assertEqual(self.client.post('/health/live').status_code, 405)
        self.assertEqual(self.client.post('/health/ready').status_code, 405)
