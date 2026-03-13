import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movierecomend.settings")

django.setup()

from movie.models import Movie, Tags


def clear_movie_tags():
    Movie.objects.all().delete()
    Tags.objects.all().delete()
