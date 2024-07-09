from django.core.management import BaseCommand
from services.mailshots.senders import MailshotSender


class Command(BaseCommand):
    help = "Запуск рассылки вручную"

    def add_arguments(self, parser):
        parser.add_argument(
            nargs="+",
            type=int,
            dest='args'
        )

    def handle(self, *args, **options):
        pk = args[0]
        response = MailshotSender(pk=pk)()

        self.stdout.write(str(response))
