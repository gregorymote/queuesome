import logging

from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET


logger = logging.getLogger(__name__)


def _health_response(payload, status=200):
    response = JsonResponse(payload, status=status)
    response['Cache-Control'] = 'no-store'
    return response


@require_GET
def live(request):
    return _health_response({'status': 'ok'})


@require_GET
def ready(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except DatabaseError:
        logger.exception('Readiness database check failed.')
        return _health_response(
            {'status': 'unavailable', 'database': 'unavailable'},
            status=503,
        )
    return _health_response({'status': 'ok', 'database': 'ok'})
