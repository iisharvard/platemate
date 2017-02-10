import os, sys
from django.conf import settings
from PIL import Image

def photo_url_for_processed_photo_upload(photo, sub_dir, photo_name):
    photo_dir_name = os.path.join(settings.STATIC_DOC_ROOT, sub_dir)
    photo_path = os.path.join(settings.STATIC_DOC_ROOT, sub_dir, 'raw', photo_name)

    try:
        os.makedirs(photo_dir_name)
    except os.error:
        pass

    destination = open(photo_path, 'wb+')
    for chunk in photo.chunks():
        destination.write(chunk)
    destination.close()

    # Original image
    original = Image.open(photo_path)

    # Resize it to 400px wide (usually 300 high)
    width, height = original.size
    new_size = 400, int(height * 400.0 / width)
    smaller = original.resize(new_size, Image.ANTIALIAS)

    # Save it to photos directory
    out_dir = os.path.join(settings.STATIC_DOC_ROOT, sub_dir,'resized')
    try:
        os.makedirs(out_dir)
    except os.error:
        pass

    out_path = os.path.join(out_dir,photo_name)
    smaller.save(out_path)

    saved_photo_url = '%s/static/%s/resized/%s' % (settings.URL_PATH, sub_dir, photo_name)
    return saved_photo_url
