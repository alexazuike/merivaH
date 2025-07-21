#!/bin/bash

cd ~/healthapp/ && source .env && git pull "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/alexazuike/healthapp.git"

cd ~ && sudo rsync -av -i --exclude '.git' --exclude 'migrations' --exclude '.env' --exclude 'static' ~/healthapp/ /opt/healthapp_be/healthapp/
cd ~ && sudo rsync -av -i --exclude '.git' --exclude 'migrations' --exclude '.env' --exclude 'static' ~/healthapp/ /opt/healthapp_be/healthapp_prod/
echo "\n\nMERGE COMPLETE"


