import re
import time

from django.core.management.base import BaseCommand

from movie.models import Tags

ZH_PATTERN = re.compile(r"[\u4e00-\u9fff]")


def has_chinese(text):
    return bool(text and ZH_PATTERN.search(text))


class Command(BaseCommand):
    help = "Translate only Chinese tag names to English; leave already-English tags unchanged."

    def handle(self, *args, **options):
        try:
            from deep_translator import GoogleTranslator
        except ImportError:
            self.stderr.write("Install deep_translator: pip install deep-translator")
            return

        translator = GoogleTranslator(source="zh-CN", target="en")
        tags = list(Tags.objects.all())
        to_translate = [t for t in tags if has_chinese(t.name)]
        self.stdout.write("Total tags: %d, with Chinese to translate: %d" % (len(tags), len(to_translate)))

        for i, tag in enumerate(to_translate, start=1):
            original = tag.name
            try:
                translated = translator.translate(original)
                tag.name = translated
                tag.save(update_fields=["name"])
                self.stdout.write("[%d/%d] %r -> %r" % (i, len(to_translate), original, translated))
                time.sleep(0.2)
            except Exception as e:
                self.stderr.write("Skip %r: %s" % (original, e))

        self.stdout.write(self.style.SUCCESS("Done. Only Chinese tags were translated."))
