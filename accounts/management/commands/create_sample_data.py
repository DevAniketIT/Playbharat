from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from accounts.models import Channel
from videos.models import Video, Playlist
from interactions.models import Comment, Like, Follow
from faker import Faker
import random
import uuid

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Create sample data for PlayBharat platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of users to create'
        )
        parser.add_argument(
            '--videos',
            type=int,
            default=50,
            help='Number of videos to create'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        with transaction.atomic():
            # Create users
            users = self.create_users(options['users'])
            self.stdout.write(f'Created {len(users)} users')
            
            # Create channels
            channels = self.create_channels(users)
            self.stdout.write(f'Created {len(channels)} channels')
            
            # Create videos
            videos = self.create_videos(channels, options['videos'])
            self.stdout.write(f'Created {len(videos)} videos')
            
            # Create playlists
            playlists = self.create_playlists(users, videos)
            self.stdout.write(f'Created {len(playlists)} playlists')
            
            # Create interactions
            self.create_interactions(users, videos)
            self.stdout.write('Created user interactions')
            
        self.stdout.write(
            self.style.SUCCESS('Sample data created successfully!')
        )

    def create_users(self, count):
        users = []
        
        for i in range(count):
            # Create unique username to avoid conflicts
            username = f'user_{fake.user_name()}{i}'[:30]  # Limit username length
            
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(minimum_age=16, maximum_age=70),
                bio=fake.text(max_nb_chars=200),
                preferred_language=random.choice(['en', 'hi', 'ta', 'te', 'bn']),
                country=fake.country_code(),
                state=fake.state(),
                city=fake.city()[:50],  # Limit city length
            )
            users.append(user)
            
        return users

    def create_channels(self, users):
        channels = []
        
        # Create channels for 70% of users
        for user in random.sample(users, int(len(users) * 0.7)):
            channel = Channel.objects.create(
                user=user,
                name=f'{fake.company()} Channel',
                handle=f'@{fake.user_name()}{random.randint(100, 999)}',
                description=fake.text(max_nb_chars=300),
                category=random.choice([
                    'entertainment', 'music', 'sports', 'news', 'education',
                    'gaming', 'comedy', 'lifestyle', 'technology', 'cooking'
                ]),
                language=random.choice(['en', 'hi', 'ta', 'te', 'bn']),
                is_verified=random.choice([True, False]) if random.random() < 0.1 else False,
            )
            channels.append(channel)
            
        return channels

    def create_videos(self, channels, count):
        videos = []
        
        video_categories = [
            'entertainment', 'music', 'sports', 'news', 'education',
            'gaming', 'comedy', 'lifestyle', 'technology', 'cooking'
        ]
        
        for i in range(count):
            channel = random.choice(channels)
            
            video = Video.objects.create(
                title=fake.sentence(nb_words=6),
                slug=f'{fake.slug()}-{uuid.uuid4().hex[:8]}',
                description=fake.text(max_nb_chars=500),
                uploader=channel.user,
                channel=channel,
                category=random.choice(video_categories),
                language=channel.language,
                duration=random.randint(60, 3600),  # 1 minute to 1 hour
                view_count=random.randint(0, 100000),
                like_count=random.randint(0, 5000),
                dislike_count=random.randint(0, 500),
                comment_count=random.randint(0, 1000),
                tags=', '.join(fake.words(nb=5)),
                visibility='public',
                allow_comments=random.choice([True, False]),
                allow_likes=random.choice([True, False]),
                is_published=True,
            )
            videos.append(video)
            
        return videos

    def create_playlists(self, users, videos):
        playlists = []
        
        for user in random.sample(users, int(len(users) * 0.5)):
            for _ in range(random.randint(1, 3)):
                playlist = Playlist.objects.create(
                    title=fake.sentence(nb_words=4),
                    description=fake.text(max_nb_chars=200),
                    user=user,
                    visibility=random.choice(['public', 'unlisted', 'private']),
                )
                
                # Add random videos to playlist
                playlist_videos = random.sample(videos, random.randint(3, 10))
                playlist.videos.set(playlist_videos)
                
                playlists.append(playlist)
                
        return playlists

    def create_interactions(self, users, videos):
        # Create likes
        for video in videos:
            likers = random.sample(users, random.randint(0, len(users) // 3))
            for user in likers:
                Like.objects.get_or_create(
                    user=user,
                    content_type_id=1,  # Assuming Video content type
                    object_id=video.id,
                    defaults={'like_type': random.choice(['like', 'dislike'])}
                )
        
        # Create comments
        for video in random.sample(videos, int(len(videos) * 0.8)):
            commenters = random.sample(users, random.randint(1, 10))
            for user in commenters:
                Comment.objects.create(
                    video=video,
                    user=user,
                    content=fake.text(max_nb_chars=200),
                    is_approved=True,
                )
        
        # Create follows
        for user in users:
            # Each user follows 3-10 other users
            followees = random.sample([u for u in users if u != user], 
                                    random.randint(3, min(10, len(users) - 1)))
            for followee in followees:
                Follow.objects.get_or_create(
                    follower=user,
                    following=followee
                )

    def get_sample_categories(self):
        return [
            'entertainment', 'music', 'sports', 'news', 'education',
            'gaming', 'comedy', 'lifestyle', 'technology', 'cooking',
            'travel', 'fitness', 'beauty', 'diy', 'reviews'
        ]