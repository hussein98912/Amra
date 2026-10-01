from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create default admin user if it does not exist"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        email = "myAdmin@example.com"
        password = "Admin@123"

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Admin {email} already exists."
                )
            )
            return

        User.objects.create_superuser(
            email=email,
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Admin {email} created successfully."
            )
        )