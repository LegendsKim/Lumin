"""Django management command to assign tenants to users without one."""
from django.core.management.base import BaseCommand
from apps.accounts.models import User, Tenant


class Command(BaseCommand):
    help = 'Assign tenants to users who do not have one'

    def handle(self, *args, **options):
        """Execute the command."""
        # Find users without tenant
        users_without_tenant = User.objects.filter(tenant__isnull=True)
        count = users_without_tenant.count()

        self.stdout.write(f'Found {count} users without tenant')

        if count == 0:
            self.stdout.write(self.style.SUCCESS('All users already have tenants assigned!'))
            return

        for user in users_without_tenant:
            # Create a tenant for this user
            tenant = Tenant.objects.create(
                business_name=f"{user.first_name} {user.last_name}'s Business",
                owner_email=user.email,
                owner_phone=user.phone if user.phone else '+972500000000',
                plan='BASIC'
            )

            # Assign tenant to user
            user.tenant = tenant
            user.save()

            self.stdout.write(
                self.style.SUCCESS(f'✅ Created tenant "{tenant.business_name}" for user {user.email}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Successfully assigned tenants to {count} users')
        )
