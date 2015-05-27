import StringIO
from datetime import datetime
import logging
from PIL import Image
from google.appengine.api import urlfetch, images
from google.appengine.api.app_identity import app_identity
from google.appengine.api.blobstore import blobstore
from google.appengine.api.namespace_manager import namespace_manager
import cloudstorage
from methods.rendering import timestamp

__author__ = 'dvpermyakov'

MAX_SIZE = 960.0
ICON_SIZE = 128.0
_BUCKET = app_identity.get_default_gcs_bucket_name()


def _resize(image, size):
    width, height = image.size
    logging.info("image size is %sx%s", width, height)
    if width > size or height > size:
        ratio = min(size / width, size / height)
        new_size = int(width * ratio), int(height * ratio)
        logging.info("resizing to %sx%s", *new_size)
        image = image.resize(new_size, Image.ANTIALIAS)
    return image


def _save(image, filename):
    image_file = cloudstorage.open(filename, "w", 'image/jpeg')
    try:
        image.save(image_file, 'JPEG')
    except:
        logging.warning('can not save JPG')
        image_file.close()
        return False
    return True


def _get_serving_url(image, filename):
    blob_key = blobstore.create_gs_key("/gs" + filename)
    serving_url = images.get_serving_url(blob_key, size=max(image.size))
    logging.info(serving_url)
    return serving_url


def _get_filename(model_name, id, uniq):
    tmstmp = timestamp(datetime.utcnow())
    return '/%s/%s/%s/%s/%s/%s' % (_BUCKET, namespace_manager.get_namespace(), model_name, id, uniq, tmstmp)


def resize_image(item, url, size=None, icon=False):
    logging.info('----------------------------------')
    logging.info('initial url = %s' % url)
    response = urlfetch.fetch(url, deadline=30)
    logging.info("image fetched, status is %s", response.status_code)
    if response.status_code == 200:  # new or updated image
        logging.info("image is new or modified")
        image_data = response.content

        image = Image.open(StringIO.StringIO(image_data))
        image = _resize(image, size)

        filename = _get_filename('MenuItem', item.key.id(), size)
        success = _save(image, filename)
        if success:
            serving_url = _get_serving_url(image, filename)

            if not icon:
                item.cut_picture = serving_url
            else:
                item.icon = serving_url
            item.put()


def save_item_image(item, image_data):
    image = Image.open(StringIO.StringIO(image_data))
    image = _resize(image, MAX_SIZE)

    filename = _get_filename('MenuItem', item.key.id(), 'init')
    success = _save(image, filename)
    if success:
        serving_url = _get_serving_url(image, filename)
        item.picture = serving_url
        item.put()