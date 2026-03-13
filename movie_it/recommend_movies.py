# -*-coding:utf-8-*-
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "movie.settings"
import django

django.setup()
from movie.models import *
from math import sqrt, pow
import operator
from django.db.models import Subquery,Q,Count


# from django.shortcuts import render,render_to_response
class UserCf:

    def __init__(self, all_user):
        self.all_user = all_user

    def getItems(self, username1, username2):
        return self.all_user[username1], self.all_user[username2]

    def pearson(self, user1, user2):
        sum_xy = 0.0
        n = 0
        sum_x = 0.0
        sum_y = 0.0
        sumX2 = 0.0
        sumY2 = 0.0
        for movie1, score1 in user1.items():
            if movie1 in user2.keys():
                n += 1
                sum_xy += score1 * user2[movie1]
                sum_x += score1
                sum_y += user2[movie1]
                sumX2 += pow(score1, 2)
                sumY2 += pow(user2[movie1], 2)
        if n == 0:
            return 0
        molecule = sum_xy - (sum_x * sum_y) / n
        denominator = sqrt((sumX2 - pow(sum_x, 2) / n) * (sumY2 - pow(sum_y, 2) / n))
        if denominator == 0:
            return 0
        r = molecule / denominator
        return r

    def nearest_user(self, current_user, n=1):
        distances = {}
        for user, rate_set in self.all_user.items():
            if user != current_user:
                distance = self.pearson(self.all_user[current_user], self.all_user[user])
                distances[user] = distance
        closest_distance = sorted(
            distances.items(), key=operator.itemgetter(1), reverse=True
        )
        print("closest user:", closest_distance[:n])
        return closest_distance[:n]

    def recommend(self, username, n=3):
        recommend = {}
        nearest_user = self.nearest_user(username, n)
        for user, score in dict(nearest_user).items():  
            for movies, scores in self.all_user[user].items(): 
                if movies not in self.all_user[username].keys():  
                    if movies not in recommend.keys():  
                        recommend[movies] = scores*score
    
        return sorted(recommend.items(), key=operator.itemgetter(1), reverse=True)


def recommend_by_user_id(user_id):
    user_prefer = UserTagPrefer.objects.filter(user_id=user_id).order_by('-score').values_list('tag_id', flat=True)
    current_user = User.objects.get(id=user_id)
    if current_user.rate_set.count() == 0:
        if len(user_prefer) != 0:
            movie_list = Movie.objects.filter(tags__in=user_prefer)[:15]
        else:
            movie_list = Movie.objects.order_by("-num")[:15]
        return movie_list
    users_rate = Rate.objects.values('user').annotate(mark_num=Count('user')).order_by('-mark_num')
    user_ids = [user_rate['user'] for user_rate in users_rate]
    user_ids.append(user_id)
    users = User.objects.filter(id__in=user_ids)
    all_user = {}
    for user in users:
        rates = user.rate_set.all()
        rate = {}
        if rates:
            for i in rates:
                rate.setdefault(str(i.movie.id), i.mark)
            all_user.setdefault(user.username, rate)
        else:
            all_user.setdefault(user.username, {})

    user_cf = UserCf(all_user=all_user)
    recommend_list = [each[0] for each in user_cf.recommend(current_user.username, 15)]
    movie_list = list(Movie.objects.filter(id__in=recommend_list).order_by("-num")[:15])
    other_length = 15 - len(movie_list)
    if other_length > 0:
        fix_list = Movie.objects.filter(~Q(rate__user_id=user_id)).order_by('-collect')
        for fix in fix_list:
            if fix not in movie_list:
                movie_list.append(fix)
            if len(movie_list) >= 15:
                break
    return movie_list



def similarity(movie1_id, movie2_id):
    movie1_set = Rate.objects.filter(movie_id=movie1_id)
    movie1_sum = movie1_set.count()
    movie2_sum = Rate.objects.filter(movie_id=movie2_id).count()
    common = Rate.objects.filter(user_id__in=Subquery(movie1_set.values('user_id')), movie=movie2_id).values('user_id').count()
    if movie1_sum == 0 or movie2_sum == 0:
        return 0
    similar_value = common / sqrt(movie1_sum * movie2_sum)
    return similar_value


def recommend_by_item_id(user_id, k=15):
    user_prefer = UserTagPrefer.objects.filter(user_id=user_id).order_by('-score').values_list('tag_id', flat=True)
    user_prefer = list(user_prefer)[:3]
    current_user = User.objects.get(id=user_id)
    if current_user.rate_set.count() == 0:
        if len(user_prefer) != 0:
            movie_list = Movie.objects.filter(tags__in=user_prefer)[:15]
        else:
            movie_list = Movie.objects.order_by("-num")[:15]
        print('from here')
        return movie_list
    un_watched = Movie.objects.filter(~Q(rate__user_id=user_id), tags__in=user_prefer).order_by('?')[:30]
    watched = Rate.objects.filter(user_id=user_id).values_list('movie_id', 'mark')
    distances = []
    names = []
    for un_watched_movie in un_watched:
        for watched_movie in watched:
            if un_watched_movie not in names:
                names.append(un_watched_movie)
                distances.append((similarity(un_watched_movie.id, watched_movie[0]) * watched_movie[1], un_watched_movie))
    distances.sort(key=lambda x: x[0], reverse=True)
    print('this is distances', distances[:15])
    recommend_list = []
    for mark, movie in distances:
        if len(recommend_list) >= k:
            break
        if movie not in recommend_list:
            recommend_list.append(movie)
    print('recommend list', recommend_list)
    return recommend_list


if __name__ == '__main__':
    similarity(2003, 2008)
    recommend_by_item_id(1)
