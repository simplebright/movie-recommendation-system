import time

from django.core.management.base import BaseCommand

from movie.models import Tags


class Command(BaseCommand):
    help = "Translate all Tags.name from Chinese to English using deep_translator."

    def handle(self, *args, **options):
        try:
            from deep_translator import GoogleTranslator
        except ImportError:
            self.stderr.write("Install deep_translator: pip install deep-translator")
            return

        translator = GoogleTranslator(source="zh-CN", target="en")
        tags = list(Tags.objects.all())
        total = len(tags)
        self.stdout.write("Total tags: %d" % total)

        for i, tag in enumerate(tags, start=1):
            original = tag.name
            try:
                translated = translator.translate(original)
                tag.name = translated
                tag.save(update_fields=["name"])
                self.stdout.write("[%d/%d] %r -> %r" % (i, total, original, translated))
                time.sleep(0.2)
            except Exception as e:
                self.stderr.write("Skip %r: %s" % (original, e))

        self.stdout.write(self.style.SUCCESS("Done translating tags."))
