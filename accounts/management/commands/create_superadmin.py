"""
Professional management command to create a super admin for PlayBharat
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a professional super admin user for PlayBharat platform'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Admin username')
        parser.add_argument('--email', type=str, help='Admin email')
        parser.add_argument('--password', type=str, help='Admin password')
        parser.add_argument('--first-name', type=str, help='Admin first name')
        parser.add_argument('--last-name', type=str, help='Admin last name')
        parser.add_argument('--force', action='store_true', help='Force create even if user exists')

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🇮🇳 PlayBharat Professional Admin Creation Tool')
        )
        self.stdout.write('=' * 50)

        # Get user input if not provided via arguments
        username = options.get('username') or input('Enter admin username: ')
        email = options.get('email') or input('Enter admin email: ')
        first_name = options.get('first_name') or input('Enter first name: ')
        last_name = options.get('last_name') or input('Enter last name: ')
        password = options.get('password')
        
        if not password:
            import getpass
            password = getpass.getpass('Enter admin password: ')
            password_confirm = getpass.getpass('Confirm password: ')
            
            if password != password_confirm:
                self.stdout.write(self.style.ERROR('Passwords do not match!'))
                return

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            self.stdout.write(self.style.ERROR('Invalid email address!'))
            return

        # Check if user exists
        if User.objects.filter(username=username).exists():
            if not options.get('force'):
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" already exists. Use --force to override.')
                )
                return
            else:
                User.objects.filter(username=username).delete()
                self.stdout.write(
                    self.style.WARNING(f'Deleted existing user "{username}"')
                )

        # Create superuser
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                country='India',
                preferred_language='en',
                email_verified=True,
                phone_verified=True,
                is_creator=False
            )
            
            self.stdout.write('=' * 50)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Super Admin created successfully!')
            )
            self.stdout.write(f'Username: {user.username}')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'Name: {user.first_name} {user.last_name}')
            self.stdout.write('=' * 50)
            self.stdout.write(
                self.style.SUCCESS('Admin can now access /admin/ with full platform control!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            )