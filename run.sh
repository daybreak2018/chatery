#! /bin/bash
./chattery_environment/bin/python ./chatery/app.py --host 0.0.0.0 --port 8266 --tz ${1:-GMT} &
caddy &
