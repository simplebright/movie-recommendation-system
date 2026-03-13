# Movie Recommendation System

Django-based movie recommendation system with collaborative filtering (user-based and item-based).

## Tech stack

- **Backend:** Python, Django 2.2
- **Database:** SQLite3
- **Frontend:** Bootstrap, jQuery

## Run locally

```bash
cd "path/to/CinemaRank"
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-run.txt
python manage.py migrate
python manage.py runserver
```

- Site: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/ (create superuser: `python manage.py createsuperuser`)

## Features

- Browse movies, search, filter by tags
- User registration, login, profile
- Rate and collect movies, comment
- User-based and item-based recommendations
- “Search on Google” link on movie page opens Google search for that movie title
