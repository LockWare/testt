#!/bin/bash
sudo gunicorn --workers=4 -b 0.0.0.0:5013 --preload --chdir /home/printedftp/rbxservers/ app:app