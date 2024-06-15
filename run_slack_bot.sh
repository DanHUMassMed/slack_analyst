#!/usr/bin/env bash
echo $1
if [ "$1" == "" ]; then
   PORT=5000
else
   PORT=$1
fi

NUM_WORKERS=3
TIMEOUT=120
PIDFILE="gunicorn.pid"

exec gunicorn researcher_app:app \
--workers $NUM_WORKERS \
--worker-class gevent \
--timeout $TIMEOUT \
--log-level=debug \
--bind=0.0.0.0:$PORT \
--pid=$PIDFILE
