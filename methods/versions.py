import re
from models import IOS_DEVICE, ANDROID_DEVICE


def get_platform_and_version(request):
    ua = request.user_agent
    match = re.match('DoubleB/([0-9.]+)', ua)
    if not match:
        return None, 0

    parts = match.group(1).split('.') + ['0', '0']
    version = int(parts[0]) * 10000 + int(parts[1]) * 100 + int(parts[2])

    if 'iOS' in ua:
        return IOS_DEVICE, version
    elif 'Android' in ua:
        return ANDROID_DEVICE, version
    else:
        return None, version


def supports_new_menu(request):
    platform, version = get_platform_and_version(request)
    return not (platform == IOS_DEVICE and version < 10301)


def supports_check_order_success(request):
    platform, version = get_platform_and_version(request)
    if platform == IOS_DEVICE:
        return version >= 10200
    elif platform == ANDROID_DEVICE:
        return version > 10300
    else:
        return False
