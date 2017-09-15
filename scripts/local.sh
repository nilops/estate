#!/bin/bash

RETRIES=5

# This will fail the first time onstartup but it takes long enough for the container to come up
# Every other time you restart the container the DB will exist and it'll work properly untill the postgress container goes away
until psql -c "select 1" > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
  echo "Waiting for postgres server, $((RETRIES--)) remaining attempts..."
  sleep 1
done

echo "Starting Webpack Server"
webpack-dev-server --config webpack/webpack.local.config.js &
echo "Starting Django Server"
django-admin migrate
django-admin loaddata initial_data
exec django-admin runserver 0.0.0.0:8000
