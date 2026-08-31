#!/usr/bin/env bash

pip install -r requirements.txt

python engine/manage.py collectstatic --noinput

python engine/manage.py migrate