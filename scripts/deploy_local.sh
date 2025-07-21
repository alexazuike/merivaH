#!/bin/bash

# deploy test
source /opt/virtualenvs/healthapp/bin/activate && cd /opt/healthapp_be/healthapp && python manage.py makemigrations && python manage.py migrate
sudo systemctl restart healthapp.service

# deploy production
source /opt/virtualenvs/healthapp/bin/activate && cd /opt/healthapp_be/healthapp_prod && python manage.py makemigrations && python manage.py migrate
sudo systecmctl restart healthapp_prod.service
