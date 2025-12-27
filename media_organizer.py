"""
Media organizer module for organizing pictures and videos into YYYYMMDD folders.
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple
from PIL import Image
from PIL.ExifTags import TAGS
import cv2

# Supported media extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.heif', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}


def get_media_date(file_path: str) -> datetime:
    """
    Extract creation date from media file.
    Tries multiple methods: EXIF data, file metadata, file modification time.
    """
    file_path_obj = Path(file_path)
    
    # Try EXIF data for images
    if file_path_obj.suffix.lower() in IMAGE_EXTENSIONS:
        try:
            image = Image.open(file_path)
            exifdata = image.getexif()
            if exifdata:
                # Try to get DateTimeOriginal (tag 36867) or DateTime (tag 306)
                for tag_id, value in exifdata.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'DateTimeOriginal' or tag == 'DateTime':
                        try:
                            return datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
                        except:
                            pass
        except Exception:
            pass
    
    # Try video metadata
    if file_path_obj.suffix.lower() in VIDEO_EXTENSIONS:
        try:
            cap = cv2.VideoCapture(file_path)
            if cap.isOpened():
                # Try to get creation date from video metadata
                # This is platform-dependent and may not always work
                pass
            cap.release()
        except Exception:
            pass
    
    # Fallback to file modification time
    try:
        mtime = os.path.getmtime(file_path)
        return datetime.fromtimestamp(mtime)
    except Exception:
        # Last resort: current date
        return datetime.now()


def create_date_folder(base_path: str, date: datetime) -> str:
    """Create a folder with YYYYMMDD format."""
    folder_name = date.strftime('%Y%m%d')
    folder_path = os.path.join(base_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def organize_media(source_dir: str, dest_dir: str, copy_files: bool = True) -> List[Tuple[str, str]]:
    """
    Organize media files into YYYYMMDD folders.
    
    Args:
        source_dir: Directory containing source media files
        dest_dir: Base directory for organized media
        copy_files: If True, copy files; if False, move files
    
    Returns:
        List of tuples (source_path, dest_path) for organized files
    """
    os.makedirs(dest_dir, exist_ok=True)
    organized_files = []
    
    source_path = Path(source_dir)
    all_extensions = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
    
    # Find all media files
    media_files = []
    for ext in all_extensions:
        media_files.extend(source_path.rglob(f'*{ext}'))
        media_files.extend(source_path.rglob(f'*{ext.upper()}'))
    
    print(f"Found {len(media_files)} media files to organize...")
    
    for media_file in media_files:
        try:
            # Get creation date
            date = get_media_date(str(media_file))
            
            # Create date folder
            date_folder = create_date_folder(dest_dir, date)
            
            # Destination path
            dest_path = os.path.join(date_folder, media_file.name)
            
            # Handle duplicate names
            counter = 1
            base_dest = dest_path
            while os.path.exists(dest_path):
                name_parts = os.path.splitext(base_dest)
                dest_path = f"{name_parts[0]}_{counter}{name_parts[1]}"
                counter += 1
            
            # Copy or move file
            if copy_files:
                shutil.copy2(media_file, dest_path)
            else:
                shutil.move(str(media_file), dest_path)
            
            organized_files.append((str(media_file), dest_path))
            print(f"Organized: {media_file.name} -> {os.path.basename(date_folder)}/")
            
        except Exception as e:
            print(f"Error organizing {media_file}: {e}")
    
    return organized_files

