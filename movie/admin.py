from django.contrib import admin
from .models import Comment, LikeComment, Movie, Rate, Tags, User, UserTagPrefer


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "director", "country", "years", "d_rate", "d_rate_nums", "num")
    list_filter = ("country", "years", "tags")
    search_fields = ("name", "director", "intro")


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "created_time")
    search_fields = ("username", "email")


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "movie", "mark", "create_time")
    list_select_related = ("user", "movie")
    list_filter = ("create_time",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "movie", "content", "create_time")
    list_select_related = ("user", "movie")
    search_fields = ("content",)
    list_filter = ("create_time",)


@admin.register(LikeComment)
class LikeCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "comment")
    list_select_related = ("user", "comment")


@admin.register(UserTagPrefer)
class UserTagPreferAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tag", "score")
    list_select_related = ("user", "tag")
