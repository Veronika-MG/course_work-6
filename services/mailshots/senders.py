from smtplib import SMTPException

from mailshots.models import Log, MailshotPeriodicTask
from services.general.messages.senders import EmailSenderMixin


class MailshotSender(EmailSenderMixin):
    """
    Класс, инкапсулирующий в себе логику механизма рассылки
    """
    def __init__(self, pk):
        self.mailshot = MailshotPeriodicTask.objects.get(pk=pk)

    def get_recipients(self) -> list:
        return self.mailshot.clients.values_list("email", flat=True)

    def get_message_content(self) -> dict:
        return {
            "subject": self.mailshot.message.subject,
            "message": self.mailshot.message.body,
        }

    def send(self):
        try:
            response = super().send()
            status = Log.Status.OK
        except SMTPException:
            response = "Error"
            status = Log.Status.FAIL

        Log.objects.create(mailshot=self.mailshot,
                           status=status,
                           response=response,
                           user=self.mailshot.user,
                           )
        return f"{status} | response: {response}"
