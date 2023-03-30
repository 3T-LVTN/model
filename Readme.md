## Running app local
* `$ uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

## Running celery local
* `$ celery worker -E -A app.main.celery --loglevel=INFO --pool=solo`