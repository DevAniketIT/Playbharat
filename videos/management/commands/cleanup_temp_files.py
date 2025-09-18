from django.core.management.base import BaseCommand
from videos.utils import clean_temp_files

class Command(BaseCommand):
    help = 'Clean up temporary video processing files'
    
    def handle(self, *args, **options):
        self.stdout.write('Cleaning up temporary files...')
        clean_temp_files()
        self.stdout.write(
            self.style.SUCCESS('Successfully cleaned up temporary files!')
        )