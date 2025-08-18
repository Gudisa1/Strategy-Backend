#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Postgres started!"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
