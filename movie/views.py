import json
import random
from functools import wraps

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer

from movie_it.cache_keys import USER_CACHE, ITEM_CACHE
from movie_it.recommend_movies import recommend_by_user_id, recommend_by_item_id
from .forms import *


def movies_paginator(movies, page):
    paginator = Paginator(movies, 12)
    if page is None:
        page = 1
    movies = paginator.page(page)
    return movies


# from django.urls import HT
# json response
class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs["content_type"] = "application/json;"
        super(JSONResponse, self).__init__(content, **kwargs)


def login(request):
    if request.method == "POST":
        form = Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            result = User.objects.filter(username=username)
            if result:
                user = User.objects.get(username=username)
                if user.password == password:
                    request.session["login_in"] = True
                    request.session["user_id"] = user.id
                    request.session["name"] = username
                    new = request.session.get('new')
                    if new:
                        tags = Tags.objects.all()
                        print('goto choose tag')
                        return render(request, 'choose_tag.html', {'tags': tags})
                    return redirect(reverse("index"))
                else:
                    return render(
                        request, "login.html", {"form": form, "errormsg": "Wrong password"}
                    )
            else:
                return render(
                    request, "login.html", {"form": form, "errormsg": "User not found"}
                )
    else:
        form = Login()
        return render(request, "login.html", {"form": form})


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        error = None
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password2"]
            email = form.cleaned_data["email"]
            User.objects.create(
                username=username,
                password=password,
                email=email,
            )
            request.session['new'] = 'true'
            return redirect(reverse("login"))
        else:
            return render(
                request, "register.html", {"form": form, "error": error}
            )
    form = RegisterForm()
    return render(request, "register.html", {"form": form})


def logout(request):
    if not request.session.get("login_in", None):
        return redirect(reverse("index"))
    request.session.flush()
    return redirect(reverse("index"))


def login_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        is_login = request.session.get("login_in")
        if is_login:
            return func(*args, **kwargs)
        else:
            return redirect(reverse("login"))

    return wrapper


# Create your views here.
def index(request):
    order =  request.POST.get("order") or request.session.get('order')
    request.session['order']=order
    if order == 'collect':
        movies = Movie.objects.annotate(collectors=Count('collect')).order_by('-collectors')
        print(movies.query)
        title = 'By collection'
    elif order == 'rate':
        movies = Movie.objects.all().annotate(marks=Avg('rate__mark')).order_by('-marks')
        title = 'By rating'
    elif order == 'years':
        movies = Movie.objects.order_by('-years')
        title = 'By date'
    else:
        movies = Movie.objects.order_by('-num')
        title = 'By popularity'
    paginator = Paginator(movies, 8)
    new_list = Movie.objects.order_by('-years')[:8]
    current_page = request.GET.get("page", 1)
    movies = paginator.page(current_page)
    return render(request, 'items.html', {'movies': movies, 'new_list': new_list, 'title': title})

def movie(request, movie_id):
    movie = Movie.objects.get(pk=movie_id)
    movie.num += 1
    movie.save()
    comments = movie.comment_set.order_by("-create_time")
    user_id = request.session.get("user_id")
    movie_rate = Rate.objects.filter(movie=movie).all().aggregate(Avg('mark'))
    if movie_rate:
        movie_rate = movie_rate['mark__avg']
    else:
        movie_rate = 0
    if user_id is not None:
        user_rate = Rate.objects.filter(movie=movie, user_id=user_id).first()
        user = User.objects.get(pk=user_id)
        is_collect = movie.collect.filter(id=user_id).first()
    return render(request, "movie.html", locals())


def search(request):
    if request.method == "POST":
        key = request.POST["search"]
        request.session["search"] = key
    else:
        key = request.session.get("search")
    movies = Movie.objects.filter(
        Q(name__icontains=key) | Q(intro__icontains=key) | Q(director__icontains=key)
    )
    page_num = request.GET.get("page", 1)
    movies = movies_paginator(movies, page_num)
    return render(request, "items.html", {"movies": movies, 'title': 'Search results'})

def all_tags(request):
    tags = Tags.objects.all()
    return render(request, "all_tags.html", {'all_tags': tags})

def one_tag(request, one_tag_id):
    tag = Tags.objects.get(id=one_tag_id)
    movies = tag.movie_set.all()
    page_num = request.GET.get("page", 1)
    movies = movies_paginator(movies, page_num)
    return render(request, "items.html", {"movies": movies, 'title': tag.name})

def hot_movie(request):
    page_number = request.GET.get("page", 1)
    movies = Movie.objects.annotate(user_collector=Count('collect')).order_by('-user_collector')[:10]
    movies = movies_paginator(movies[:10], page_number)
    return render(request, "items.html", {"movies": movies, "title": "Most collected"})


def most_mark(request):
    page_number = request.GET.get("page", 1)
    movies = Movie.objects.all().annotate(num_mark=Count('rate')).order_by('-num_mark')
    movies = movies_paginator(movies, page_number)
    return render(request, "items.html", {"movies": movies, "title": "Top rated"})


def most_view(request):
    page_number = request.GET.get("page", 1)
    movies = Movie.objects.annotate(user_collector=Count('num')).order_by('-num')
    movies = movies_paginator(movies, page_number)
    return render(request, "items.html", {"movies": movies, "title": "Most viewed"})

def latest_movie(request):
    movie_list = Movie.objects.order_by("-years")[:10]
    json_movies = [movie.to_dict(fields=['name', 'image_link', 'id', 'years', 'd_rate']) for movie in movie_list]
    return HttpResponse(json.dumps(json_movies), content_type="application/json")


def director_movie(request, director_name):
    page_number = request.GET.get("page", 1)
    movies = Movie.objects.filter(director=director_name)
    movies = movies_paginator(movies, page_number)
    return render(request, "items.html", {"movies": movies, "title": "Director: {}".format(director_name)})

@login_in
def personal(request):
    user = User.objects.get(id=request.session.get("user_id"))
    if request.method == "POST":
        form = Edit(instance=user, data=request.POST)
        if form.is_valid():
            form.save()
            request.session['name'] = user.username
            return render(
                request, "personal.html", {"message": "Saved.", "form": form, 'title': 'Profile', 'user': user}
            )
        else:
            return render(
                request, "personal.html", {"message": "Save failed.", "form": form, 'title': 'Profile', 'user': user}
            )
    form = Edit(instance=user)
    return render(request, "personal.html", {"user": user, 'form': form, 'title': 'Profile'})


@login_in
@csrf_exempt
def choose_tags(request):
    tags_name = json.loads(request.body)
    user_id = request.session.get('user_id')
    for tag_name in tags_name:
        tag = Tags.objects.filter(name=tag_name.strip()).first()
        UserTagPrefer.objects.create(tag_id=tag.id, user_id=user_id, score=5)
    request.session.pop('new')
    return redirect(reverse("index"))


@login_in
def make_comment(request, movie_id):
    user = User.objects.get(id=request.session.get("user_id"))
    movie = Movie.objects.get(id=movie_id)
    comment = request.POST.get("comment")
    Comment.objects.create(user=user, movie=movie, content=comment)
    return redirect(reverse("movie", args=(movie_id,)))


@login_in
def my_comments(request):
    user = User.objects.get(id=request.session.get("user_id"))
    comments = user.comment_set.all()
    return render(request, "my_comment.html", {"item": comments})


@login_in
def like_comment(request, comment_id, movie_id):
    user_id = request.session.get("user_id")
    LikeComment.objects.get_or_create(user_id=user_id, comment_id=comment_id)
    return redirect(reverse("movie", args=(movie_id,)))


@login_in
def unlike_comment(request, comment_id, movie_id):
    user_id = request.session.get("user_id")
    LikeComment.objects.filter(user_id=user_id, comment_id=comment_id).delete()
    return redirect(reverse("movie", args=(movie_id,)))


@login_in
def delete_comment(request, comment_id):
    Comment.objects.get(pk=comment_id).delete()
    return redirect(reverse("my_comments"))


@login_in
def score(request, movie_id):
    user_id = request.session.get("user_id")
    # user = User.objects.get(id=user_id)
    movie = Movie.objects.get(id=movie_id)
    score = float(request.POST.get("score"))
    get, created = Rate.objects.get_or_create(user_id=user_id, movie=movie, defaults={"mark": score})
    if created:
        for tag in movie.tags.all():
            prefer, created = UserTagPrefer.objects.get_or_create(user_id=user_id, tag=tag, defaults={'score': score})
            if not created:
                prefer.score += (score - 3)
                prefer.save()
        user_cache = USER_CACHE.format(user_id=user_id)
        item_cache = ITEM_CACHE.format(user_id=user_id)
        cache.delete(user_cache)
        cache.delete(item_cache)
    return redirect(reverse("movie", args=(movie_id,)))

@login_in
def my_rate(request):
    user = User.objects.get(id=request.session.get("user_id"))
    rate = user.rate_set.all()
    return render(request, "my_rate.html", {"item": rate})


@login_in
def delete_rate(request, rate_id):
    Rate.objects.filter(pk=rate_id).delete()
    return redirect(reverse("my_rate"))

@login_in
def collect(request, movie_id):
    user = User.objects.get(id=request.session.get("user_id"))
    movie = Movie.objects.get(id=movie_id)
    movie.collect.add(user)
    movie.save()
    return redirect(reverse("movie", args=(movie_id,)))

@login_in
def decollect(request, movie_id):
    user = User.objects.get(id=request.session.get("user_id"))
    movie = Movie.objects.get(id=movie_id)
    movie.collect.remove(user)
    movie.save()
    return redirect(reverse("movie", args=(movie_id,)))

@login_in
def mycollect(request):
    user = User.objects.get(id=request.session.get("user_id"))
    movie = user.movie_set.all()
    return render(request, "mycollect.html", {"item": movie})

def user_recommend(request):
    user_id = request.session.get("user_id")
    if user_id is None:
        movie_list = Movie.objects.order_by('?')
    else:
        cache_key = USER_CACHE.format(user_id=user_id)
        movie_list = cache.get(cache_key)
        if movie_list is None:
            movie_list = recommend_by_user_id(user_id)
            cache.set(cache_key, movie_list, 60 * 5)

    json_movies = [movie.to_dict(fields=['name', 'image_link', 'id', 'years', 'd_rate']) for movie in movie_list]
    random.shuffle(json_movies)
    return HttpResponse(json.dumps(json_movies[:3]), content_type="application/json")

def item_recommend(request):
    user_id = request.session.get("user_id")
    if user_id is None:
        movie_list = Movie.objects.order_by('?')
    else:
        cache_key = ITEM_CACHE.format(user_id=user_id)
        movie_list = cache.get(cache_key)
        if movie_list is None:
            movie_list = recommend_by_item_id(user_id)
            cache.set(cache_key, movie_list, 60 * 5)
    json_movies = [movie.to_dict(fields=['name', 'image_link', 'id', 'years', 'd_rate']) for movie in movie_list]
    random.shuffle(json_movies)
    return HttpResponse(json.dumps(json_movies[:3]), content_type="application/json")
