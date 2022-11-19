clock: rqscheduler --queue-class=CustomQueue.CustomQueue --url=${RQ_REDIS_URL} --interval=.5
web: gunicorn views:flaskapp
