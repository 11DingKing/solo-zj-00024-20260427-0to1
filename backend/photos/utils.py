import os
import io
import exifread
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings


THUMBNAIL_SIZES = {
    'small': {'size': (150, 150), 'crop': True},
    'medium': {'size': (400, 400), 'crop': False},
    'large': {'size': (800, 800), 'crop': False},
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file_size(file_obj):
    file_obj.seek(0, os.SEEK_END)
    size = file_obj.tell()
    file_obj.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024 * 1024)}MB")
    return size


def generate_thumbnails(image_field, photo_instance):
    try:
        image = Image.open(image_field)
        image.verify()
        image = Image.open(image_field)
        
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        original_width, original_height = image.size
        photo_instance.image_width = original_width
        photo_instance.image_height = original_height
        
        for size_name, size_config in THUMBNAIL_SIZES.items():
            target_size = size_config['size']
            crop = size_config['crop']
            
            thumb_image = image.copy()
            
            if crop:
                thumb_image = crop_center(thumb_image, target_size[0], target_size[1])
            else:
                thumb_image.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            thumb_io = io.BytesIO()
            thumb_image.save(thumb_io, format='JPEG', quality=85, optimize=True)
            thumb_io.seek(0)
            
            original_name = os.path.basename(image_field.name)
            name_without_ext = os.path.splitext(original_name)[0]
            thumb_filename = f"{name_without_ext}_{size_name}.jpg"
            
            thumb_field = getattr(photo_instance, f'thumbnail_{size_name}')
            thumb_field.save(thumb_filename, ContentFile(thumb_io.read()), save=False)
            
    except Exception as e:
        print(f"Error generating thumbnails: {e}")
        raise


def crop_center(image, target_width, target_height):
    width, height = image.size
    
    aspect_ratio = width / height
    target_aspect = target_width / target_height
    
    if aspect_ratio > target_aspect:
        new_width = int(height * target_aspect)
        left = (width - new_width) // 2
        top = 0
        right = left + new_width
        bottom = height
    else:
        new_height = int(width / target_aspect)
        left = 0
        top = (height - new_height) // 2
        right = width
        bottom = top + new_height
    
    image = image.crop((left, top, right, bottom))
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)


def extract_exif_data(image_field):
    exif_data = {}
    
    try:
        image_field.seek(0)
        tags = exifread.process_file(image_field, details=False)
        
        if 'Image Make' in tags:
            exif_data['exif_camera_make'] = str(tags['Image Make'])
        
        if 'Image Model' in tags:
            exif_data['exif_camera_model'] = str(tags['Image Model'])
        
        if 'EXIF LensModel' in tags:
            exif_data['exif_lens_model'] = str(tags['EXIF LensModel'])
        
        if 'EXIF FocalLength' in tags:
            focal_length = str(tags['EXIF FocalLength'])
            exif_data['exif_focal_length'] = f"{focal_length}mm"
        
        if 'EXIF FNumber' in tags:
            f_number = eval(str(tags['EXIF FNumber']))
            exif_data['exif_aperture'] = f"f/{f_number}"
        
        if 'EXIF ExposureTime' in tags:
            exposure = str(tags['EXIF ExposureTime'])
            exif_data['exif_shutter_speed'] = f"{exposure}s"
        
        if 'EXIF ISOSpeedRatings' in tags:
            exif_data['exif_iso'] = int(str(tags['EXIF ISOSpeedRatings']))
        
        if 'EXIF Flash' in tags:
            flash_value = str(tags['EXIF Flash'])
            exif_data['exif_flash'] = 'Flash fired' in flash_value
        
        if 'EXIF WhiteBalance' in tags:
            wb = str(tags['EXIF WhiteBalance'])
            exif_data['exif_white_balance'] = 'Auto' if wb == '0' else 'Manual'
        
        if 'EXIF DateTimeOriginal' in tags:
            from datetime import datetime
            date_str = str(tags['EXIF DateTimeOriginal'])
            try:
                exif_data['exif_datetime_original'] = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            except:
                pass
        
        gps_lat = extract_gps_coordinate(tags, 'GPS GPSLatitude', 'GPS GPSLatitudeRef')
        gps_lon = extract_gps_coordinate(tags, 'GPS GPSLongitude', 'GPS GPSLongitudeRef')
        
        if gps_lat is not None:
            exif_data['exif_gps_latitude'] = gps_lat
        if gps_lon is not None:
            exif_data['exif_gps_longitude'] = gps_lon
        
        if 'GPS GPSAltitude' in tags:
            try:
                altitude = eval(str(tags['GPS GPSAltitude']))
                exif_data['exif_gps_altitude'] = float(altitude)
            except:
                pass
                
    except Exception as e:
        print(f"Error extracting EXIF data: {e}")
    
    return exif_data


def extract_gps_coordinate(tags, coord_tag, ref_tag):
    if coord_tag not in tags or ref_tag not in tags:
        return None
    
    try:
        coord_values = tags[coord_tag].values
        ref = str(tags[ref_tag])
        
        degrees = float(coord_values[0].num) / float(coord_values[0].den)
        minutes = float(coord_values[1].num) / float(coord_values[1].den)
        seconds = float(coord_values[2].num) / float(coord_values[2].den)
        
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        
        if ref in ['S', 'W']:
            decimal = -decimal
            
        return decimal
    except:
        return None
