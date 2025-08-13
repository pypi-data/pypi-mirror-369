from typing import Dict

from django.http.request import HttpRequest

from .utils import get_source_revision


REVISION = get_source_revision()


def static_revision(request: HttpRequest) -> Dict[str, str]:
    return {'REVISION': REVISION}
