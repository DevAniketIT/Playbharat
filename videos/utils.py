import os
import uuid
import subprocess
from pathlib import Path
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Handles video processing including validation, thumbnail generation, and format conversion"""
    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
        self.max_file_size = getattr(settings, 'MAX_VIDEO_FILE_SIZE', 2 * 1024 * 1024 * 1024)  # 2GB
        
    def validate_video_file(self, video_file):
        """Validate video file format and size"""
        errors = []
        
        # Check file size
        if video_file.size > self.max_file_size:
            errors.append(f'Video file too large. Maximum size is {self.max_file_size // (1024*1024*1024)}GB.')
        
        # Check file extension
        file_ext = Path(video_file.name).suffix.lower()
        if file_ext not in self.supported_formats:
            errors.append(f'Unsupported video format. Supported formats: {", ".join(self.supported_formats)}')
        
        return errors
    
    def generate_thumbnail(self, video_file, output_path=None, timestamp='00:00:01'):
        """Generate thumbnail from video using ffmpeg"""
        try:
            # Create a temporary file path for the video
            temp_video_path = self._save_temp_video(video_file)
            
            if not output_path:
                thumbnail_filename = f"thumb_{uuid.uuid4().hex}.jpg"
                output_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', thumbnail_filename)
            
            # Ensure thumbnails directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Use ffmpeg to extract thumbnail
            cmd = [
                'ffmpeg',
                '-i', temp_video_path,
                '-ss', timestamp,
                '-vframes', '1',
                '-q:v', '2',  # High quality
                '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2',
                '-y',  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temporary video file
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return None
            
            if os.path.exists(output_path):
                # Return relative path from MEDIA_ROOT
                relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
                return relative_path.replace('\\', '/')  # Ensure forward slashes for URLs
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            return None
    
    def get_video_info(self, video_file):
        """Extract video metadata using ffmpeg"""
        try:
            temp_video_path = self._save_temp_video(video_file)
            
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                temp_video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temporary video file
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            
            if result.returncode != 0:
                logger.error(f"FFprobe error: {result.stderr}")
                return {}
            
            import json
            info = json.loads(result.stdout)
            
            # Extract relevant information
            video_info = {}
            if 'format' in info:
                video_info['duration'] = float(info['format'].get('duration', 0))
                video_info['size'] = int(info['format'].get('size', 0))
            
            # Find video stream
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_info['width'] = stream.get('width', 0)
                    video_info['height'] = stream.get('height', 0)
                    video_info['codec'] = stream.get('codec_name', '')
                    video_info['fps'] = self._parse_framerate(stream.get('r_frame_rate', ''))
                    break
            
            return video_info
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return {}
    
    def _save_temp_video(self, video_file):
        """Save uploaded video to temporary location for processing"""
        temp_filename = f"temp_{uuid.uuid4().hex}{Path(video_file.name).suffix}"
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', temp_filename)
        
        # Ensure temp directory exists
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        # Save video file
        with open(temp_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
        
        return temp_path
    
    def _parse_framerate(self, framerate_str):
        """Parse framerate from ffprobe output"""
        try:
            if '/' in framerate_str:
                num, den = framerate_str.split('/')
                return float(num) / float(den)
            return float(framerate_str)
        except:
            return 0.0

    def create_multiple_thumbnails(self, video_file, count=3):
        """Generate multiple thumbnails at different timestamps"""
        video_info = self.get_video_info(video_file)
        duration = video_info.get('duration', 60)
        
        thumbnails = []
        
        # Generate thumbnails at different intervals
        for i in range(count):
            timestamp_seconds = (duration / (count + 1)) * (i + 1)
            timestamp = f"{int(timestamp_seconds // 60):02d}:{int(timestamp_seconds % 60):02d}"
            
            thumbnail_path = self.generate_thumbnail(video_file, timestamp=timestamp)
            if thumbnail_path:
                thumbnails.append(thumbnail_path)
        
        return thumbnails

class ImageProcessor:
    """Handle image processing for thumbnails and profile pictures"""
    
    def __init__(self):
        self.max_image_size = getattr(settings, 'MAX_IMAGE_FILE_SIZE', 5 * 1024 * 1024)  # 5MB
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    def validate_image_file(self, image_file):
        """Validate image file"""
        errors = []
        
        # Check file size
        if image_file.size > self.max_image_size:
            errors.append(f'Image file too large. Maximum size is {self.max_image_size // (1024*1024)}MB.')
        
        # Check file extension
        file_ext = Path(image_file.name).suffix.lower()
        if file_ext not in self.supported_formats:
            errors.append(f'Unsupported image format. Supported formats: {", ".join(self.supported_formats)}')
        
        return errors
    
    def resize_image(self, image_file, max_width=1920, max_height=1080, quality=85):
        """Resize and optimize image"""
        try:
            # Open image
            image = Image.open(image_file)
            
            # Convert RGBA to RGB if necessary (for JPEG)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Calculate new dimensions
            width, height = image.size
            if width > max_width or height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            from io import BytesIO
            output = BytesIO()
            
            # Determine format
            format = 'JPEG'
            if hasattr(image_file, 'name'):
                if image_file.name.lower().endswith('.png'):
                    format = 'PNG'
                    quality = None  # PNG doesn't use quality parameter
            
            if quality:
                image.save(output, format=format, quality=quality, optimize=True)
            else:
                image.save(output, format=format, optimize=True)
            
            output.seek(0)
            
            # Create new ContentFile
            filename = f"optimized_{uuid.uuid4().hex}.{format.lower()}"
            return ContentFile(output.getvalue(), name=filename)
            
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            return None

def clean_temp_files():
    """Clean up old temporary files"""
    try:
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        if os.path.exists(temp_dir):
            import time
            current_time = time.time()
            
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    # Delete files older than 1 hour
                    if current_time - os.path.getmtime(file_path) > 3600:
                        os.remove(file_path)
                        logger.info(f"Cleaned up temp file: {filename}")
    except Exception as e:
        logger.error(f"Error cleaning temp files: {str(e)}")

# Utility functions
def get_video_duration_display(seconds):
    """Convert seconds to MM:SS or HH:MM:SS format"""
    if not seconds:
        return "0:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def generate_unique_filename(original_filename):
    """Generate unique filename while preserving extension"""
    ext = Path(original_filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return unique_name

def check_ffmpeg_availability():
    """Check if FFmpeg is available on the system"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False