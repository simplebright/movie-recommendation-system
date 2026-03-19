import os
import sys
from pathlib import Path


def _env(name: str) -> str | None:
    v = os.environ.get(name)
    return v.strip() if v and v.strip() else None


def main() -> int:
    """
    Render-friendly bootstrap:
    - creates/updates a Django admin superuser using env vars
    - safe to run on every boot (idempotent)

    Required env vars:
      DJANGO_SUPERUSER_USERNAME
      DJANGO_SUPERUSER_EMAIL
      DJANGO_SUPERUSER_PASSWORD
    """
    # Ensure project root is on sys.path (Render runs from repo root, but be safe).
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movierecomend.settings")

    username = _env("DJANGO_SUPERUSER_USERNAME")
    email = _env("DJANGO_SUPERUSER_EMAIL")
    password = _env("DJANGO_SUPERUSER_PASSWORD")
    if not (username and email and password):
        # Nothing to do.
        return 0

    import django  # noqa: WPS433 (runtime import is intentional for bootstrap)

    django.setup()

    from django.contrib.auth import get_user_model  # noqa: WPS433

    User = get_user_model()
    user, _created = User.objects.get_or_create(username=username, defaults={"email": email})
    # Always enforce correct privileges + password so you can log in.
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

