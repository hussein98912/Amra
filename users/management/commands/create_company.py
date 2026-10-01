from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from companies.models import Company


class Command(BaseCommand):
    help = "Create default company user and company if they do not exist"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        email = "myCompany@example.com"
        password = "Company@123"

        # Check if company user already exists
        user = User.objects.filter(email=email).first()

        if user:
            self.stdout.write(
                self.style.WARNING(
                    f"Company user {email} already exists."
                )
            )

            # Make sure role is COMPANY
            if user.role != "COMPANY":
                user.role = "COMPANY"

            user.is_active = True
            user.save()

        else:
            # Create company user
            user = User.objects.create_user(
                email=email,
                password=password,
                role="COMPANY",
                full_name="Default Company",
            )

            user.is_active = True
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Company user {email} created successfully."
                )
            )

        # Check if this user already owns a company
        company = Company.objects.filter(owner=user).first()

        if company:
            self.stdout.write(
                self.style.WARNING(
                    f"Company already exists: {company.name}"
                )
            )
        else:
            company = Company.objects.create(
                owner=user,
                name="Default Company",
                license_number="DEFAULT-LICENSE",
                phone="+0000000000",
                address="Default Address",
                status="ACTIVE",
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Company created successfully: {company.name}"
                )
            )

        # Link the user to the company
        if user.company_id != company.id:
            user.company = company
            user.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Company setup completed successfully."
            )
        )