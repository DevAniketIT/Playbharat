from django.core.management.base import BaseCommand
from django.conf import settings
from videos.models import Video
import os
import re
from difflib import SequenceMatcher

class Command(BaseCommand):
    help = 'Fix video thumbnails by mapping existing thumbnail files to videos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get the thumbnails directory path
        thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
        
        if not os.path.exists(thumbnails_dir):
            self.stdout.write(
                self.style.ERROR(f'Thumbnails directory not found: {thumbnails_dir}')
            )
            return

        # Get all thumbnail files
        thumbnail_files = []
        for filename in os.listdir(thumbnails_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                thumbnail_files.append(filename)

        self.stdout.write(f'Found {len(thumbnail_files)} thumbnail files')

        # Get videos without thumbnails using Q objects
        from django.db.models import Q
        videos_without_thumbnails = Video.objects.filter(
            Q(thumbnail__isnull=True) | Q(thumbnail='')
        )

        self.stdout.write(f'Found {videos_without_thumbnails.count()} videos without thumbnails')

        # Create title-to-filename mapping
        title_mappings = {
            # Exact matches found in thumbnail files
            'Amazing Indian Street Food Tour': 'amazing_indian_street_food_tour_thumbnail.jpeg',
            'Art: Indian Painting Tutorial': 'art_indian_painting_tutorial_thumbnail.jpeg',
            'Bollywood Music Mix 2024': 'bollywood_music_mix_2024_thumbnail.jpeg',
            'Business Tips for Startups': 'business_tips_for_startups_thumbnail.jpeg',
            'Classical Dance Performance': 'classical_dance_performance_thumbnail.jpeg',
            'Comedy Sketch Show': 'comedy_sketch_show_thumbnail.jpeg',
            'Cooking Traditional Biryani': 'cooking_traditional_biryani_thumbnail.jpeg',
            'Cooking with Python': 'cooking_with_python_thumbnail.jpeg',
            'Cricket Highlights 2024': 'cricket_highlights_2024_thumbnail.jpeg',
            'Culture: Festival Celebrations': 'culture_festival_celebrations_thumbnail.jpeg',
            'Educational: Science Explained': 'educational_science_explained_thumbnail.jpeg',
            'Fashion: Traditional Wear': 'fashion_traditional_wear_thumbnail.jpeg',
            'Fitness: Yoga for Beginners': 'fitness_yoga_for_beginners_thumbnail.jpeg',
            'Gaming Review: Best Games of 2024': 'gaming_best_games_2024_thumbnail.jpeg',
            'Gaming: Popular Mobile Games': 'gaming_popular_mobile_games_thumbnail.jpeg',
            'Health: Ayurvedic Medicine': 'health_ayurvedic_medicine_thumbnail.jpeg',
            'Healthy Cooking Tips': 'healthy_cooking_tips_thumbnail.jpeg',
            'History: Ancient Indian Civilization': 'history_ancient_indian_civilization_thumbnail.jpeg',
            'Introduction to Django': 'introduction_to_django_thumbnail.jpeg',
            'Music: Folk Songs Collection': 'music_folk_songs_collection_thumbnail.jpeg',
            'Music Theory Basics': 'music_theory_basics_thumbnail.jpeg',
            'News Update: Technology Trends': 'news_technology_trends_thumbnail.jpeg',
            'Sports: Football Skills': 'sports_football_skills_thumbnail.jpeg',
            'Tech Review: Latest Smartphone': 'tech_review_latest_smartphone_thumbnail.jpeg',
            'Technology: AI in India': 'technology_ai_in_india_thumbnail.jpeg',
            'Travel Vlog: Incredible India': 'travel_vlog_incredible_india_thumbnail.jpeg'
        }

        updated_count = 0
        no_match_count = 0
        
        # Keep track of used thumbnails to avoid conflicts
        used_thumbnails = set()
        
        # Get already used thumbnails
        videos_with_thumbnails = Video.objects.exclude(
            Q(thumbnail__isnull=True) | Q(thumbnail='')
        )
        for v in videos_with_thumbnails:
            if v.thumbnail:
                thumbnail_name = os.path.basename(str(v.thumbnail))
                used_thumbnails.add(thumbnail_name)
        
        # Get available unused thumbnails
        available_thumbnails = [f for f in thumbnail_files if f not in used_thumbnails]
        
        self.stdout.write(f'Available unused thumbnails: {len(available_thumbnails)}')

        for video in videos_without_thumbnails:
            matched_filename = None
            
            # First try exact mapping
            if video.title in title_mappings:
                matched_filename = title_mappings[video.title]
            else:
                # Try to find the best match using string similarity
                best_match = None
                best_ratio = 0
                
                video_title_clean = self.clean_title_for_matching(video.title)
                
                for filename in thumbnail_files:
                    filename_clean = self.clean_filename_for_matching(filename)
                    ratio = SequenceMatcher(None, video_title_clean, filename_clean).ratio()
                    
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_match = filename
                
                # Only use match if similarity is high enough
                if best_ratio > 0.6:
                    matched_filename = best_match
                    self.stdout.write(
                        self.style.WARNING(
                            f'Auto-matched "{video.title}" -> "{matched_filename}" (similarity: {best_ratio:.2f})'
                        )
                    )

            if matched_filename:
                thumbnail_path = f'thumbnails/{matched_filename}'
                
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'[DRY RUN] Would update "{video.title}" -> {thumbnail_path}'
                        )
                    )
                else:
                    video.thumbnail = thumbnail_path
                    video.save(update_fields=['thumbnail'])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated "{video.title}" -> {thumbnail_path}'
                        )
                    )
                updated_count += 1
            else:
                # Fallback: assign any available thumbnail
                if available_thumbnails:
                    fallback_thumbnail = available_thumbnails.pop(0)  # Take the first available
                    thumbnail_path = f'thumbnails/{fallback_thumbnail}'
                    
                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(
                                f'[DRY RUN] Would assign fallback thumbnail "{video.title}" -> {thumbnail_path}'
                            )
                        )
                    else:
                        video.thumbnail = thumbnail_path
                        video.save(update_fields=['thumbnail'])
                        self.stdout.write(
                            self.style.WARNING(
                                f'Assigned fallback thumbnail "{video.title}" -> {thumbnail_path}'
                            )
                        )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'No thumbnail available for: "{video.title}"'
                        )
                    )
                    no_match_count += 1

        # Summary
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'[DRY RUN] Would update {updated_count} videos, {no_match_count} without matches'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} videos with thumbnails'
                )
            )
            if no_match_count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'{no_match_count} videos still need manual thumbnail assignment'
                    )
                )

    def clean_title_for_matching(self, title):
        """Clean video title for matching"""
        # Remove special characters, convert to lowercase, replace spaces with underscores
        cleaned = re.sub(r'[^\w\s]', '', title.lower())
        cleaned = re.sub(r'\s+', '_', cleaned)
        return cleaned

    def clean_filename_for_matching(self, filename):
        """Clean filename for matching"""
        # Remove _thumbnail.jpeg suffix and clean
        cleaned = filename.replace('_thumbnail.jpeg', '')
        cleaned = cleaned.replace('_thumbnail.jpg', '')
        cleaned = cleaned.replace('_thumbnail.png', '')
        return cleaned