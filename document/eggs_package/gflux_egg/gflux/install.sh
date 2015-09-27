#!/bin/sh

easy_install -Z lib/dash-*.egg
cp config/local_settings.py.local local_settings.py
