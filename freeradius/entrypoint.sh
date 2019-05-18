#!/usr/bin/env bash

sed -i "s/{MYSQL_DATABASE}/$MYSQL_DATABASE/g" /etc/raddb/mods-enabled/sql
sed -i "s/{MYSQL_ROOT_PASSWORD}/$MYSQL_ROOT_PASSWORD/g" /etc/raddb/mods-enabled/sql

./docker-entrypoint.sh