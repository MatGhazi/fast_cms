from os import getenv


SECRET_KEY = 'f457<m58/f4r#44>&9'
TEST_HASH = b'$2b$16$cY211KyW2aqzYQmGnn0ZGuX4Xyp4ZnHod7AI29aLXMKK2cc547E7q'
HASHING_COST = int(getenv('HASHING_COST', 12))
MAX_SESSION_COUNT = 5
DELETION_BREAK_IN_DAYS = 7


class OTP:
    length = 6
    wait = 2
    expiry = 10


class IMAGE:
    full_size = 1280
    full_quality = 90
    thumbnail_size = 360
    thumbnail_quality = 70
    is_public = False


class AVATAR(IMAGE):
    full_size = 800
    thumbnail_size = 120
    is_public = True


