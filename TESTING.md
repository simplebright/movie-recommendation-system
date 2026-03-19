## Testing (1-page summary)

### Test approach
- **Scope**: Django unit tests for core course requirements: authentication/access control, database-backed features, and user input validation/feedback.
- **Method**: `django.test.TestCase` with an isolated test database (SQLite). Tests use Django’s test client and URL reversing to exercise views end-to-end.
- **Coverage focus**:
  - **Access control**: protected pages require login; logout clears session.
  - **User input used by the app**: tag preferences are submitted via JSON and stored; Home content is filtered by stored preferences.
  - **Validation and feedback**: empty/invalid inputs return clear error messages.

### Unit tests implemented (Django required)
Location: `movie/tests.py`

- **Auth and access control**
  - `test_logout_flushes_session`: verifies `/logout/` clears the session and redirects.
  - `test_protected_page_redirects_when_not_logged_in`: verifies protected page `/personal/` redirects to `/login/` when not authenticated.

- **Tag preference (core feature)**
  - `test_choose_tags_requires_login`: POST to `/choose_tags/` redirects to login when not authenticated.
  - `test_choose_tags_rejects_empty_selection`: empty tag submission returns HTTP 400 with JSON `{ ok: false }`.
  - `test_choose_tags_saves_preferences_and_replaces_old`: new tag selection overwrites previous preferences.
  - `test_home_filters_movies_by_preferred_tags`: Home (`/`) lists movies matching the user’s preferred tags and excludes non-matching ones.

- **Search validation**
  - `test_search_empty_input_shows_message`: blank search shows “Please enter a search term …” feedback on the results page.

### How to run the tests (for TAs)
From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-run.txt
python manage.py migrate
python manage.py test
```

### Test results (automated)
All tests pass locally:

```text
Found 7 test(s).
.......
Ran 7 tests in 0.02s
OK
```

*(For submission evidence, run `python manage.py test` and screenshot the terminal output above.)*

