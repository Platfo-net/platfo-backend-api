from django.core.management.base import BaseCommand
import os
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            User.objects.get(
                username=os.environ.get('FIRST_ADMIN_USERNAME', 'admin'))
        except User.DoesNotExist:
            user = User.objects.create(
                username=os.environ.get('FIRST_ADMIN_USERNAME', 'admin'),
                email=os.environ.get('FIRST_ADMIN_EMAIL', 'admin@gmail.com'),
                is_staff=True,
                is_active=True,
                is_superuser=True
            )
            user.set_password(os.environ.get('FIRST_ADMIN_PASSWORD', 'admin'))

            user.save()
