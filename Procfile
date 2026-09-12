release: python manage.py migrate --noinput
web: gunicorn queue_it_up.wsgi:application --log-file -
worker: python manage.py process_tasks --queue game --sleep 1 --log-std
