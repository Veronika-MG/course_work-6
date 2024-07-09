from celery import shared_task
from services.mailshots.senders import MailshotSender


@shared_task
def send_mailshot(pk):
    MailshotSender(pk=pk)()


