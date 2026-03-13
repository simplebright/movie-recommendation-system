import os
import time

import django
from deep_translator import GoogleTranslator


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movierecomend.settings")
django.setup()

from movie.models import Tags  # noqa: E402


def main() -> None:
    translator = GoogleTranslator(source="zh-CN", target="en")
    tags = list(Tags.objects.all())
    total = len(tags)
    print(f"Total tags: {total}")

    for idx, tag in enumerate(tags, start=1):
        original = tag.name
        try:
            translated = translator.translate(original)
            tag.name = translated
            tag.save(update_fields=["name"])
            print(f"[{idx}/{total}] {original!r} -> {translated!r}")
            time.sleep(0.2)
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] failed to translate {original!r}: {exc}")

    print("Done translating tags.")


if __name__ == "__main__":
    main()

