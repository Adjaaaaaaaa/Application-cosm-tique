"""
Management command to manage Premium dev mode for development.
"""

import os
from django.core.management.base import BaseCommand, CommandError
from common.premium_utils import get_development_environment_info


class Command(BaseCommand):
    help = 'Manage Premium dev mode for development purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['status', 'enable', 'disable', 'check', 'list-authorized', 'add-authorized', 'remove-authorized'],
            help='Action to perform: status, enable, disable, check, list-authorized, add-authorized, or remove-authorized'
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username to add/remove from authorized developers list'
        )

    def handle(self, *args, **options):
        action = options['action']
        username = options.get('username')

        if action == 'status':
            self.show_status()
        elif action == 'enable':
            self.enable_dev_mode()
        elif action == 'disable':
            self.disable_dev_mode()
        elif action == 'check':
            self.check_environment()
        elif action == 'list-authorized':
            self.list_authorized_users()
        elif action == 'add-authorized':
            if not username:
                raise CommandError("Username is required for add-authorized action")
            self.add_authorized_user(username)
        elif action == 'remove-authorized':
            if not username:
                raise CommandError("Username is required for remove-authorized action")
            self.remove_authorized_user(username)

    def show_status(self):
        """Show current Premium dev mode status."""
        env_info = get_development_environment_info()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('PREMIUM DEV MODE STATUS')
        self.stdout.write('='*60)
        
        self.stdout.write(f'🔧 Virtual Environment: {"✅ Yes" if env_info["is_virtual_environment"] else "❌ No"}')
        self.stdout.write(f'🛠️  Development Environment: {"✅ Yes" if env_info["is_development_environment"] else "❌ No"}')
        self.stdout.write(f'🐛 Debug Mode: {"✅ Yes" if env_info["debug_mode"] else "❌ No"}')
        self.stdout.write(f'👑 Premium Dev Mode: {"✅ Enabled" if env_info["premium_dev_mode"] else "❌ Disabled"}')
        self.stdout.write(f'⚙️  Settings Module: {env_info["settings_module"]}')
        
        self.stdout.write('\n👥 Authorized Developers:')
        if env_info["authorized_dev_users"]:
            for user in env_info["authorized_dev_users"]:
                self.stdout.write(f'   ✅ {user}')
        else:
            self.stdout.write('   ❌ No authorized developers')
        
        self.stdout.write('\n📋 Environment Variables:')
        for var, value in env_info["development_vars"].items():
            status = "✅ Set" if value else "❌ Not set"
            self.stdout.write(f'   {var}: {value or "Not set"} ({status})')
        
        self.stdout.write('\n' + '='*60)

    def enable_dev_mode(self):
        """Enable Premium dev mode."""
        env_info = get_development_environment_info()
        
        # Temporarily allow enabling without virtual environment for testing
        # Note: Virtual environment check is bypassed for development convenience
        # if not env_info["is_virtual_environment"]:
        #     raise CommandError(
        #         "❌ Cannot enable Premium dev mode: Not running in a virtual environment\n"
        #         "💡 Activate your virtual environment first"
        #     )
        
        if not env_info["debug_mode"]:
            raise CommandError(
                "❌ Cannot enable Premium dev mode: DEBUG mode is disabled\n"
                "💡 Ensure DEBUG=True in your settings"
            )
        
        # Set environment variable
        os.environ['DJANGO_DEVELOPMENT'] = 'true'
        
        self.stdout.write(
            self.style.SUCCESS(
                "✅ Premium dev mode enabled!\n"
                "💡 Set DJANGO_DEVELOPMENT=true in your virtual environment\n"
                "🔄 Restart your Django server for changes to take effect\n"
                "👥 Only authorized developers will have Premium access"
            )
        )

    def disable_dev_mode(self):
        """Disable Premium dev mode."""
        # Remove environment variable
        if 'DJANGO_DEVELOPMENT' in os.environ:
            del os.environ['DJANGO_DEVELOPMENT']
        
        self.stdout.write(
            self.style.WARNING(
                "✅ Premium dev mode disabled!\n"
                "💡 Remove DJANGO_DEVELOPMENT=true from your environment\n"
                "🔄 Restart your Django server for changes to take effect"
            )
        )

    def check_environment(self):
        """Check if environment is properly configured for development."""
        env_info = get_development_environment_info()
        
        self.stdout.write('\n🔍 ENVIRONMENT CHECK')
        self.stdout.write('='*40)
        
        issues = []
        
        if not env_info["is_virtual_environment"]:
            issues.append("❌ Not running in a virtual environment")
        
        if not env_info["debug_mode"]:
            issues.append("❌ DEBUG mode is disabled")
        
        if not env_info["is_development_environment"]:
            issues.append("❌ Development environment not detected")
        
        if not env_info["premium_dev_mode"]:
            issues.append("❌ Premium dev mode is disabled")
        
        if not env_info["authorized_dev_users"]:
            issues.append("❌ No authorized developers configured")
        
        if issues:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Environment issues found:\n" + "\n".join(issues)
                )
            )
            self.stdout.write(
                "\n💡 To fix these issues:\n"
                "1. Activate your virtual environment\n"
                "2. Set DJANGO_DEVELOPMENT=true\n"
                "3. Ensure DEBUG=True in settings\n"
                "4. Add authorized developers to AUTHORIZED_DEV_USERS\n"
                "5. Restart your Django server"
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "✅ Environment is properly configured for development!\n"
                    "🎉 Premium dev mode is active and ready for testing"
                )
            )

    def list_authorized_users(self):
        """List all authorized developers."""
        env_info = get_development_environment_info()
        
        self.stdout.write('\n👥 AUTHORIZED DEVELOPERS')
        self.stdout.write('='*30)
        
        if env_info["authorized_dev_users"]:
            for i, user in enumerate(env_info["authorized_dev_users"], 1):
                self.stdout.write(f'{i}. {user}')
        else:
            self.stdout.write('❌ No authorized developers configured')
        
        self.stdout.write('\n💡 To add developers:')
        self.stdout.write('   python manage.py manage_premium_dev_mode add-authorized --username username')

    def add_authorized_user(self, username):
        """Add a user to the authorized developers list."""
        self.stdout.write(
            self.style.WARNING(
                f"⚠️  To add '{username}' to authorized developers:\n"
                "1. Edit config/settings/dev.py\n"
                "2. Add '{username}' to AUTHORIZED_DEV_USERS list\n"
                "3. Or set AUTHORIZED_DEV_USERS environment variable\n"
                "4. Restart your Django server"
            )
        )

    def remove_authorized_user(self, username):
        """Remove a user from the authorized developers list."""
        self.stdout.write(
            self.style.WARNING(
                f"⚠️  To remove '{username}' from authorized developers:\n"
                "1. Edit config/settings/dev.py\n"
                "2. Remove '{username}' from AUTHORIZED_DEV_USERS list\n"
                "3. Or set AUTHORIZED_DEV_USERS environment variable\n"
                "4. Restart your Django server"
            )
        )
