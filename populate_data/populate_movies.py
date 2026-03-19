import datetime
import os
import sys
import ast

import django

# Ensure project root is on sys.path so 'movierecomend' can be imported
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movierecomend.settings")
django.setup()

import csv
import re
from movie.models import Tags, Movie
from populate_data.clear_movies import clear_movie_tags


def parse_time(time_str):
    time = time_str.split('-')
    years = time[0]
    if len(time) > 1:
        month = time[1]
    else:
        month = 1
    if len(time) > 2:
        day = time[2]
    else:
        day = 1
    time = datetime.date(int(years), int(month), int(day))

    return str(time)


def replace_special_char(name):
    special_char = r'[\\/:*?#@！%!"<>|：\s]'
    return re.sub(special_char, '_', name)


def populate_movies(filename):
    opener = open(filename, 'r', encoding='utf-8', errors='ignore', newline='')
    reader = csv.reader(opener)
    next(reader)
    for line in reader:
        # only use the first 13 columns, ignore any extra
        cols = line[:13]
        if len(cols) < 13:
            continue
        (
            id,
            title,
            image_link,
            country,
            years,
            director_description,
            leader,
            star,
            description,
            tags,
            imdb,
            language,
            time_length,
        ) = cols

        origin_years = years
        years = re.search(pattern=r'\d{4}?(-\d{0,2})?(-\d{0,2})', string=years)
        if years is None:
            years = origin_years.split('(')[0]
        else:
            years = years[0]
        res = re.match(r'\d*', star)
        int_d_rate_num = int(res[0]) if res else 0
        pic_name = 'movie_cover/' + replace_special_char(title) + '.png'
        years = parse_time(years)
        # Store original leader string directly to avoid parsing issues with quotes
        leader_str = leader
        movie, created = Movie.objects.get_or_create(
            name=title,
            defaults={
                'image_link': pic_name,
                'country': country,
                'years': parse_time(years),
                'leader': leader_str,
                'd_rate_nums': int_d_rate_num,
                'd_rate': star,
                'intro': description,
                'director': director_description,
                'imdb_link': imdb,
            },
        )
        print('movie', movie, 'created', created)
        tags = [tag.strip() for tag in tags.split('/')]
        for tag in tags:
            tag_obj, created = Tags.objects.get_or_create(name=tag)
            print('created', created)
            movie.tags.add(tag_obj.id)
    #


if __name__ == '__main__':
    # Use absolute paths from project root to avoid path issues
    csv_top250 = os.path.join(BASE_DIR, 'csv_data', 'top250.csv')

    clear_movie_tags()
    populate_movies(csv_top250)
