import json
from datetime import date

from django.test import TestCase
from django.urls import reverse

from movie.models import Movie, Tags, User, UserTagPrefer


class BaseAppTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="pass1234", email="t@example.com")
        self.tag_drama = Tags.objects.create(name="Drama")
        self.tag_crime = Tags.objects.create(name="Crime")
        self.movie_a = Movie.objects.create(
            name="Movie A",
            director="Director A",
            country="USA",
            years=date(2020, 1, 1),
            leader="Actor A",
            d_rate_nums=100,
            d_rate="9.0",
            intro="A test movie.",
            num=0,
            image_link="movie_cover/movie_a.png",
            imdb_link="https://example.com/a",
        )
        self.movie_a.tags.add(self.tag_drama)
        self.movie_b = Movie.objects.create(
            name="Movie B",
            director="Director B",
            country="USA",
            years=date(2021, 1, 1),
            leader="Actor B",
            d_rate_nums=50,
            d_rate="8.0",
            intro="Another test movie.",
            num=0,
            image_link="movie_cover/movie_b.png",
            imdb_link="https://example.com/b",
        )
        self.movie_b.tags.add(self.tag_crime)

    def login_session(self):
        session = self.client.session
        session["login_in"] = True
        session["user_id"] = self.user.id
        session["name"] = self.user.username
        session.save()


class AuthAndAccessControlTests(BaseAppTestCase):
    def test_logout_flushes_session(self):
        self.login_session()
        resp = self.client.get(reverse("logout"))
        self.assertEqual(resp.status_code, 302)
        # After logout, session should not have login flag
        self.assertFalse(self.client.session.get("login_in", False))

    def test_protected_page_redirects_when_not_logged_in(self):
        resp = self.client.get(reverse("personal"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("login"), resp["Location"])


class TagPreferenceTests(BaseAppTestCase):
    def test_choose_tags_requires_login(self):
        resp = self.client.post(
            reverse("choose_tags"),
            data=json.dumps(["Drama"]),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("login"), resp["Location"])

    def test_choose_tags_rejects_empty_selection(self):
        self.login_session()
        resp = self.client.post(
            reverse("choose_tags"),
            data=json.dumps([]),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data["ok"])

    def test_choose_tags_saves_preferences_and_replaces_old(self):
        self.login_session()
        UserTagPrefer.objects.create(user=self.user, tag=self.tag_crime, score=5)

        resp = self.client.post(
            reverse("choose_tags"),
            data=json.dumps(["Drama"]),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["ok"])
        prefers = list(UserTagPrefer.objects.filter(user=self.user).values_list("tag__name", flat=True))
        self.assertEqual(prefers, ["Drama"])

    def test_home_filters_movies_by_preferred_tags(self):
        self.login_session()
        UserTagPrefer.objects.create(user=self.user, tag=self.tag_drama, score=5)
        resp = self.client.get(reverse("index"))
        self.assertEqual(resp.status_code, 200)
        # Should include Movie A (Drama) and exclude Movie B (Crime)
        self.assertContains(resp, "Movie A")
        self.assertNotContains(resp, "Movie B")


class SearchValidationTests(BaseAppTestCase):
    def test_search_empty_input_shows_message(self):
        resp = self.client.post(reverse("search"), data={"search": "   "})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Please enter a search term")
