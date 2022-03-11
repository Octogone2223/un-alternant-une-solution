from django.core.management import call_command
from django.contrib.staticfiles.management.commands.collectstatic import (
    Command as CollectStaticCommand,
)


class Command(CollectStaticCommand):
    def handle(self, *args, **options):
        call_command("tailwind", "start")
        super().handle(*args, **options)