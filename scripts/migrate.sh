#!/bin/bash


echo "\n\nMIGRATING TO DEFAULT DB"
python manage migrate 

echo "\n\nMIGRATING TO SANDBOX DB"
python manage migrate --database=sandbox