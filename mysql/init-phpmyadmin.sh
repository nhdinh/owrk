#!/bin/sh
set -e

if [ -f /run/secrets/mysql_root_passwd ]; then
    export MYSQL_ROOT_PASSWORD=$(cat /run/secrets/mysql_root_passwd | tr -d '[:space:]')
else
    export MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32)
fi


if [ -f /run/secrets/mysql_user_passwd ]; then
    export MYSQL_ROOT_PASSWORD=$(cat /run/secrets/mysql_user_passwd | tr -d '[:space:]')
else
    export MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32)
fi