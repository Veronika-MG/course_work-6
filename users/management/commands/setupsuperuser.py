from django.core.management import BaseCommand
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    """
    Команда создания суперпользователя
    """
    def handle(self, *args, **options):
        email = input("email: ")
        password = input("password: ")
        user = User(email=email)
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.stdout.write(self.style.SUCCESS("суперпользователь создан!"))
