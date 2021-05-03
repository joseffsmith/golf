# Golf

requirements
node >= 12 (untested)
python3 >= 3.8

## Backend setup

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
optionally remove all dependencies and let them install fresh


## Frontend setup

```
cd Frontend
npm i
```

## Running dev environment

Make sure env variables setup

### API
```
FLASK_APP=views.py:flaskapp FLASK_ENV=development python -m flask run --debugger
```

### Scheduler
Run with `heroku local` and Procfile (comment out worker/API line, don't need gunicorn for local API)

### Frontend
```
npm start
```

available at http://localhost:3000
