web: gunicorn app:app
worker: node --optimize_for_size --max_old_space_size=460 --gc_interval=100 index.js