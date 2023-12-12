#!/bin/sh

# Wait for PostgreSQL database to be ready
echo "Checking if the PostgreSQL host ($POSTGRES_HOST $POSTGRES_DB_PORT) is ready..."
until nc -z -v -w30 $POSTGRES_HOST $(( $POSTGRES_DB_PORT ));
do
    echo 'Waiting for the DB to be ready...'
    sleep 2
done


# Perform Django database migrations
python manage.py makemigrations
python manage.py migrate


# Start Django development server
python manage.py runserver 0.0.0.0:8000
