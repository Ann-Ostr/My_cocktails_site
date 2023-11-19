FROM python:3.9
#RUN mkdir /app
WORKDIR /app
RUN pip install gunicorn==20.1.0
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"];
#django-admin.py startproject foodgram; 
#CMD  cd /app/backend/foodgram; django-admin.py startproject foodgram; cd /app/backend; 
CMD python manage.py collectstatic --no-input; cp -r /app/collected_static/. /backend_static/; python manage.py migrate;  python ./recipes/management/import_to_postgresql.py; python manage.py createsuperuser --noinput; gunicorn --bind 0.0.0.0:8000 foodgram.wsgi
