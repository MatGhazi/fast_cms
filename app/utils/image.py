from datetime import datetime, UTC
from io import BytesIO
from bson import ObjectId

from fastapi import UploadFile
from PIL import Image as PILImage
from PIL import ExifTags

from app.models.media import Image
from app.settings import IMAGE
import app.database as db


def optimize(image_data, size, quality):
    image = PILImage.open(BytesIO(image_data))
    #
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation)
            if orientation_value == 3:
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:
                image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass
    #
    factor = int(size) / max(image.size)
    image_size = (int(image.size[0]*factor), int(image.size[1]*factor))
    image = image.resize(image_size, PILImage.LANCZOS)
    #
    buffer = BytesIO()
    image.save(buffer, optimize=True, quality=int(quality), format='webp')
    buffer.seek(0)
    return buffer


async def upload(
    uid: str,
    model: str,
    object_id: str,
    field: str,
    file: UploadFile,
    settings: IMAGE,
) -> str:
    if model not in [i.__name__ for i in db.MODELS]:
        raise Exception('Invalid model!')
    if field not in getattr(db, model).model_fields:
        raise Exception('Invalid field!')
    #
    file_data = await file.read()
    full = optimize(file_data, settings.full_size, settings.full_quality)
    thumbnail = optimize(file_data, settings.thumbnail_size, settings.thumbnail_quality)
    metadata={'content_type': 'image/webp'}
    full_id = await db.fs.upload_from_stream(file.filename, full, metadata=metadata)
    thumbnail_id = await db.fs.upload_from_stream(f'thumbnail_{file.filename}', thumbnail, metadata=metadata)
    #
    image = Image(
        uid=str(uid),
        model=model,
        field=field,
        object_id=object_id,
        file_name=file.filename,
        datetime=datetime.now(UTC),
        full_id=str(full_id),
        thumbnail_id=str(thumbnail_id),
        is_public=settings.is_public,
    )
    await image.create()
    return str(image.id)


async def delete(id: str, uid: str):
    image = await Image.get(id)
    #
    if not image:
        raise Exception('Image not found!')
    if image.uid != uid:
        raise Exception('Access denied!')
    #
    await db.fs.open_download_stream(ObjectId(image.full_id))
    await db.fs.open_download_stream(ObjectId(image.thumbnail_id))
    #
    await db.fs.delete(ObjectId(image.full_id))
    await db.fs.delete(ObjectId(image.thumbnail_id))
    await image.delete()
