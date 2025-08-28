**A Django automated billing system with a REST API.**

To run Celery(For PDFs):
1. celery -A silver beat --loglevel=info
2. celery -A billing_system worker --loglevel=info --pool=solo

# from your project root (venv active)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
