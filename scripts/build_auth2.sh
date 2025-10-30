#!/bin/bash

cd ./services/auth-frontend-v2
npm run build

docker cp ./dist/assets auth-fe-v2:/usr/share/nginx/html/
docker cp ./dist/index.html auth-fe-v2:/usr/share/nginx/html/
