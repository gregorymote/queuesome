release: python manage.py migrate --noinput
web: gunicorn queue_it_up.wsgi:application --log-file -
