"""Management command to assign tenants to users without one."""
from django.core.management.base import BaseCommand
from apps.authentication.models import User
from apps.core.models import Tenant


class Command(BaseCommand):
    help = 'Assign tenants to users who do not have one'

    def handle(self, *args, **options):
        users_without_tenant = User.objects.filter(tenant__isnull=True)

        if not users_without_tenant.exists():
            self.stdout.write(self.style.SUCCESS('All users already have tenants assigned'))
            return

        self.stdout.write(f'Found {users_without_tenant.count()} users without tenant')

        for user in users_without_tenant:
            # Create a tenant for this user
            tenant = Tenant.objects.create(
                name=f"{user.first_name} {user.last_name}'s Business",
                owner=user,
                plan='BASIC'  # Default plan
            )

            # Assign tenant to user
            user.tenant = tenant
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created tenant "{tenant.name}" for user {user.email}'
                )
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully assigned tenants to {users_without_tenant.count()} users'))
