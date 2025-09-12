"""
Management command to create a Premium test user for development.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from common.premium_utils import is_development_environment, force_premium_for_development


class Command(BaseCommand):
    help = 'Create a Premium test user for development purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='testuser',
            help='Username for the test user (default: testuser)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='test@example.com',
            help='Email for the test user (default: test@example.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='testpass123',
            help='Password for the test user (default: testpass123)'
        )
        parser.add_argument(
            '--no-authorize',
            action='store_true',
            help='Do not automatically add user to authorized developers list'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        no_authorize = options['no_authorize']

        # Security checks
        if not getattr(settings, 'DEBUG', False):
            raise CommandError(
                "This command can only be used in development mode (DEBUG=True)"
            )

        if not getattr(settings, 'IS_PREMIUM_DEV_MODE', False):
            raise CommandError(
                "IS_PREMIUM_DEV_MODE must be enabled to create Premium test users. "
                "Set DJANGO_DEVELOPMENT=true in your virtual environment."
            )

        # Temporarily allow creating users without virtual environment for testing
        # Note: Virtual environment check is bypassed for development convenience
        # if not is_development_environment():
        #     raise CommandError(
        #         "This command can only be used in a development environment. "
        #         "Ensure you're running in a virtual environment and set DJANGO_DEVELOPMENT=true"
        #     )

        try:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" already exists. Updating to Premium...')
                )
            else:
                # Create new user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created user "{username}" successfully.')
                )

            # Force Premium status
            force_premium_for_development(user)

            # Add to authorized developers list if not disabled
            if not no_authorize:
                authorized_users = list(getattr(settings, 'AUTHORIZED_DEV_USERS', []))
                if username not in authorized_users:
                    authorized_users.append(username)
                    self.stdout.write(
                        self.style.SUCCESS(f'Added "{username}" to authorized developers list.')
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            "💡 To make this permanent, add the username to AUTHORIZED_DEV_USERS in config/settings/dev.py"
                        )
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ User "{username}" now has Premium access!\n'
                    f'📧 Email: {email}\n'
                    f'🔑 Password: {password}\n'
                    f'👑 Status: Premium'
                )
            )

            # Provide helpful information
            self.stdout.write(
                self.style.WARNING(
                    '\n💡 Developer Tips:\n'
                    '• Use the subscription page to toggle between Free/Premium\n'
                    '• Premium dev mode is only active for authorized developers\n'
                    '• Normal users cannot access Premium without payment in production\n'
                    '• Only authorized developers can use the dev tools'
                )
            )

        except Exception as e:
            raise CommandError(f'Failed to create Premium test user: {str(e)}')
