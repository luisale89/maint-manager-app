release: pipenv run upgrade
web: gunicorn wsgi --chdir ./src/
DATABASE_URL="sqlite:////mnt/d/Desarrollo Web/flask-dev/coldy_lp/database.db"