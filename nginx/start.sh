#!/bin/bash

mkdir -p logs
envsubst < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
chmod -R 755 /frontend/build

for dir in /usr/share/nginx/*;
do
    chmod -R 755 "$dir"/
done

nginx -g 'daemon off;'