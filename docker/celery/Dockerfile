FROM python:3.10.10
WORKDIR /app
ADD .env /app/
ADD requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ADD . /app/

CMD ["celery", "worker", "-E", "-A", "app.main.celery_app"]
