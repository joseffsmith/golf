# Golf

requirements
node >= 12 (untested)
python3 >= 3.8

## Dev backend setup

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Running dev environment

### API (app)

```
/var/www/golf/env/bin/gunicorn views:flaskapp
```

### Scheduler

```
/var/www/golf/env/bin/python scheduler.py
```

### Worker

runs all the different 'queues' of jobs, 'squash', 'golf', 'brs', 'int'

```
/var/www/golf/env/bin/rq worker recurring squash golf brs int --url=${RQ_REDIS_URL} --sentry-dsn=https://3ac09515060a422c8b0fd6c72336bc6a@o4504389848137728.ingest.sentry.io/4504389849841664
```

### Frontend

in 'brs_frontend', install deps and npm run dev

## Prod setup

all the systemd scripts necessary are in 'systemd' folder, symlink them to /etc/systemd/system then restart systemd

logs can be accessed via `./manage.sh logs`

can restart services on code change via `./manage.sh restart`

frontend needs to be built from `brs_frontend`

an nginx is needed to connect all this together
