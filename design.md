# Design Specification — Movie Recommendation System

**Course:** Internet Technology (M) — Coursework 4 (Design Specification)  
**Document purpose:** Team design specification for the web application, suitable for submission or reference alongside the implementation.

---

## 1. Overview

**Application name:** Movie Recommendation System

**What it does:**  
A web application that lets users browse a movie catalogue, register and log in, set favourite genres (tags), rate and collect movies, leave comments, and receive personalised recommendations based on user-based and item-based collaborative filtering.

**Intended users:**  
General users who want to discover movies, keep a personal watchlist, and get recommendations aligned with their tastes (by tags and by similar users/items).

**Problem addressed:**  
Users often struggle to find movies that match their preferences. The app addresses this by storing user preferences (tags, ratings, collections) and using them to filter the home feed and to compute recommendations.

**Value provided:**  
- Central place to browse, search, and filter movies by tags.  
- Personal account to save ratings, collections, and comments.  
- Home page and recommendation widgets that reflect the user’s chosen tags and behaviour.  
- Clear, responsive UI (Bootstrap) and accessibility considerations (e.g. skip link, labels, ARIA).

---

## 2. Specification (Prioritised User Stories — MoSCoW)

| ID | Priority | User story |
|----|----------|------------|
| **M1** | Must | As a **visitor**, I want to **register and log in / log out**, so that **I can have a persistent identity and access personalised features**. |
| **M2** | Must | As a **logged-in user**, I want to **browse movies stored in the database** (list, detail, by tag, by director), so that **I can discover and choose what to watch**. |
| **M3** | Must | As a **logged-in user**, I want to **input and save my preferred tags**, so that **the home page and recommendations reflect my taste**. |
| **M4** | Must | As a **logged-in user**, I want to **rate movies and have that rating saved**, so that **my preferences are used for recommendations and displayed on my profile**. |
| **M5** | Must | As a **logged-in user**, I want to **add/remove movies to/from my collection**, so that **I can maintain a personal watchlist**. |
| **S1** | Should | As a **logged-in user**, I want to **search movies by title, director, or description**, so that **I can quickly find specific films**. |
| **S2** | Should | As a **logged-in user**, I want to **comment on a movie and see others’ comments**, so that **I can share and read opinions**. |
| **S3** | Should | As a **logged-in user**, I want to **edit my profile** (e.g. username, email, password), so that **my account details stay up to date**. |
| **C1** | Could | As a **user**, I want to **see user-based and item-based recommendation widgets** on the home page, so that **I discover movies similar to my taste or to ones I liked**. |
| **C2** | Could | As an **administrator**, I want to **manage movies, users, tags, and ratings in Django Admin**, so that **content and data can be maintained centrally**. |

**Must requirements coverage:**  
- **User authentication:** M1 (register, login, logout).  
- **Database-backed model interaction:** M2, M4, M5 (movies, ratings, collections).  
- **User input saved and used by the application:** M3 (tags drive home feed), M4 (ratings drive recommendations), M5 (collections stored and listed).

---

## 3. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client (Browser)                          │
│  HTML/CSS/JS (Bootstrap, jQuery), Templates (Django)             │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Django Application Server                      │
│  • URL routing (movierecomend.urls, movie views)                 │
│  • Session-based auth, @login_in access control                  │
│  • Views: index, login, register, movie detail, search,          │
│    score, comment, collect, choose_tags, personal, etc.        │
│  • Django Admin (separate auth: auth_user)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌───────────────────────┐
│  SQLite DB      │ │  Recommendation │ │  Static / Media        │
│  (db.sqlite3)   │ │  Module         │ │  (staticfiles, media)  │
│  • movie_*      │ │  (movie_it)     │ │  Admin CSS/JS, covers  │
│  • auth_*       │ │  User/Item CF   │ │                        │
└─────────────────┘ └─────────────────┘ └───────────────────────┘
```

**Components:**  
- **Client:** Browser; server-rendered HTML from Django templates; Bootstrap for layout; jQuery for AJAX (e.g. recommendations, tag submit).  
- **Django app:** Handles all routes, session-based login, and access control; serves templates and APIs (e.g. JSON for recommendations).  
- **SQLite:** Single database file; stores application models (User, Movie, Tags, Rate, Comment, etc.) and Django admin auth.  
- **Recommendation module:** `movie_it.recommend_movies` (user-based and item-based collaborative filtering) and cache keys; used by views that serve recommendation widgets.  
- **Static/Media:** `STATIC_ROOT` (e.g. admin CSS/JS, site assets) and `MEDIA_ROOT` (movie covers); served in development via Django, in production via same app or CDN/WhiteNoise.

**External APIs:**  
None required by the current design. Optional: external search (e.g. “Search on Google” link for a movie title) is outbound only and does not affect architecture.

---

## 4. ER Diagram (Compressed Chen Notation) and Entity Attributes

**Notation:** Entities in rectangles; relationships in diamonds; attributes listed per entity. Cardinalities: one-to-many (1:N), many-to-many (M:N) where applicable.

**Entities and attributes:**

| Entity       | Attributes                                                                 | Notes |
|-------------|-----------------------------------------------------------------------------|-------|
| **User**    | id (PK), username (unique), password, email, created_time                  | Application user (not Django auth_user). |
| **Tags**    | id (PK), name (unique)                                                     | Genre/category labels. |
| **Movie**   | id (PK), name (unique), director, country, years, leader (cast), d_rate, d_rate_nums, intro, num (views), origin_image_link, image_link, imdb_link | Core catalogue. |
| **Rate**    | id (PK), user_id (FK), movie_id (FK), mark, create_time                    | User’s numeric rating for a movie. |
| **Comment** | id (PK), user_id (FK), movie_id (FK), content, create_time                 | User’s text comment on a movie. |
| **UserTagPrefer** | id (PK), user_id (FK), tag_id (FK), score                          | User’s preferred tags (for home filtering and recommendations). |
| **LikeComment**  | id (PK), user_id (FK), comment_id (FK)                             | User “likes” a comment. |

**Relationships:**

- **User** —(registers / owns)— **Rate** (1:N)  
- **User** —(writes)— **Comment** (1:N)  
- **User** —(has)— **UserTagPrefer** (1:N)  
- **User** —(likes)— **LikeComment** (1:N)  
- **Movie** —(receives)— **Rate** (1:N)  
- **Movie** —(has)— **Comment** (1:N)  
- **Movie** —(has)— **Tags** (M:N, via movie_tags)  
- **Movie** —(collected by)— **User** (M:N, collect; “My collect”)  
- **Tags** —(chosen in)— **UserTagPrefer** (1:N)  
- **Comment** —(liked by)— **LikeComment** (1:N)

**Constraints:**  
- Unique (username), unique (Movie.name), unique (Tags.name).  
- Foreign keys with CASCADE where appropriate (e.g. delete user → delete their rates, comments, preferences).

---

## 5. Site Map (Pages and Must Requirements)

```
                                    ┌─────────────┐
                                    │   /admin/   │  (Django Admin — C2)
                                    └──────┬──────┘
                                           │
┌──────────┐     ┌──────────┐     ┌───────▼───────┐     ┌──────────────┐
│  /       │────▶│  /login  │────▶│  /register    │────▶│  /logout     │
│  (Home)  │◀────│  [M1]    │◀────│  [M1]         │     │  [M1]        │
└────┬─────┘     └──────────┘     └──────────────┘     └──────────────┘
     │
     │  (if not tagged)     ┌─────────────────┐
     └─────────────────────▶│  /all_tags       │  → same as tag choice [M3]
                            │  (Tags = choose  │
                            │   tags UI)       │
                            └────────┬─────────┘
                                     │ POST
                                     ▼
                            ┌─────────────────┐
                            │  /choose_tags/   │  [M3] Save preferred tags
                            └─────────────────┘

     │  (main content)
     ├───────────────────────────────────────────────────────────────────┐
     ▼                     ▼                     ▼                      ▼
┌─────────────┐   ┌─────────────────┐   ┌──────────────┐   ┌─────────────────┐
│  /movie/<id>│   │  /one_tag/<id>   │   │  /search     │   │  /director_movie │
│  [M2]       │   │  [M2]            │   │  [S1]        │   │  [M2]            │
│  Detail,    │   │  Movies by tag   │   │  Search form │   │  By director    │
│  rate [M4], │   │                  │   │              │   │                 │
│  collect    │   │                  │   │              │   │                 │
│  [M5],      │   │                  │   │              │   │                 │
│  comment    │   │                  │   │              │   │                 │
└─────────────┘   └─────────────────┘   └──────────────┘   └─────────────────┘

     │  (logged-in only)
     ├──────────────────┬──────────────────┬──────────────────┐
     ▼                  ▼                  ▼                  ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  /personal  │  │  /mycollect │  │ /my_comments│  │  /my_rate   │
│  [S3]       │  │  [M5]       │  │  [S2]       │  │  [M4]       │
│  Profile    │  │  My list    │  │  My comments│  │  My ratings │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```

**Must requirements mapping:**  
- **M1:** `/login`, `/register`, `/logout`.  
- **M2:** `/` (Home), `/movie/<id>`, `/one_tag/<id>`, `/director_movie/<name>`.  
- **M3:** `/all_tags` (tag choice UI), `/choose_tags` (save).  
- **M4:** `/movie/<id>` (rate form), `/score/<id>`, `/my_rate`.  
- **M5:** `/movie/<id>` (collect/decollect), `/mycollect`.

---

## 6. Wireframes (Main Screens)

**1. Home (index) — `/`**  
- Header: logo, search bar, nav (Home, Tags, Profile / My Collect / Logout or Login / Register, Admin).  
- Main: grid of movie cards (poster, title, year); sort dropdown (popularity, collection count, rating, date).  
- Sidebar: “Latest” list (AJAX), “User-based recommendations” (AJAX).  
- Supports: M2 (browse), M3 (home filtered by chosen tags when logged in).

**2. Login / Register**  
- Login: title “Movie Recommendation System Admin - Login”, username and password fields with visible labels, error message area (e.g. wrong password / user not found), “Login” button, link to Register.  
- Register: username, email, password, confirm password; validation messages; “Register” then redirect to Login.  
- Supports: M1.

**3. Tag selection (choose_tag / all_tags)**  
- Heading: “Choose your favorite tags”.  
- Grid of tag buttons (toggle selection; aria-pressed, visual highlight).  
- Status/error message area (e.g. “Select at least one tag”, “Preferences saved”).  
- “Submit” button; on success, redirect to Home.  
- Supports: M3.

**4. Movie detail — `/movie/<id>`**  
- Poster, title, director, cast, country, year, rating, tags (links to one_tag), description, IMDB link.  
- If logged in: rate (score input + submit), collect / uncollect, comment form; list of comments with like/delete.  
- Supports: M2, M4, M5, S2.

**5. Profile — `/personal`**  
- Form: username, email, password (edit); “Saved” / “Save failed” message.  
- Supports: S3.

*(Wireframes should be drawn in a tool (e.g. draw.io) and included in the PowerPoint/PDF submission; the above describes the corresponding screens and which requirements they cover.)*

---

## 7. Accessibility Plan (WCAG 2.2)

| # | WCAG 2.2 success criterion / topic | What it means for this application |
|---|-------------------------------------|------------------------------------|
| 1 | **Keyboard operable (2.1.1)**      | All main actions (login, register, tag selection, search, rate, collect, comment) are reachable and usable via keyboard; focus order is logical; no keyboard trap. |
| 2 | **Labels or instructions (3.3.2)** | Form fields (login, register, search, comment, rate, profile edit, tag submit) have visible or programmatically associated labels so purpose is clear to all users and assistive technologies. |
| 3 | **Info and relationships (1.3.1)**| Structure is expressed in HTML (headings, landmarks, lists) and ARIA where needed (e.g. nav, main, status/alert), so assistive technologies can understand layout and content hierarchy. |
| 4 | **Error identification / feedback (3.3.1, 4.1.3)** | Invalid input or failed actions (wrong password, empty tag submit, validation errors) produce clear, non-sensory text messages (e.g. role="alert" or aria-live) so users know what went wrong and how to fix it. |
| 5 | **Consistent navigation (3.2.3)**   | Navigation (Home, Tags, Profile, My Collect, Login/Logout, Admin) appears in the same order and position across pages (base template) to reduce cognitive load and support predictable operation. |

**Implementation notes (already applied in project):**  
- Skip link to main content; `<main id="main-content">` with `tabindex="-1"`.  
- Login/register: explicit `<label>` and error div with `role="alert"` / `aria-live`.  
- Tag selection: message region with `role="status"` and `aria-live="polite"`; buttons use `aria-pressed`.  
- Search: label (e.g. “Search movies”) and consistent nav in `base.html`.

---

## 8. Appendix (Template for Submission)

**Team member contributions (%):**  
- [To be filled: e.g. Member A 33%, Member B 33%, Member C 34%.]

**Contributions per member:**  
- [To be filled: e.g. Overview and spec, ER diagram and site map, wireframes and accessibility plan, etc.]

**AI use statement:**  
- [To be filled with one or more of the declarations from the coursework, e.g. “We declare that we have not used GenAI…” or “We declare that we have used GenAI for…”.]

---

*This design specification aligns with the implemented Movie Recommendation System (Django, SQLite, Bootstrap, session-based auth, tag-based home feed, ratings, collections, comments, and recommendations) and with the structure required by the ITECH Design Specification coursework.*
