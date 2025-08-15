from sona.settings import settings

from .base import MiddlewareBase
from .supervisors import KafkaSupervisor, SQSSupervisor

middlewares = [
    MiddlewareBase.load_class(kls)() for kls in settings.SONA_MIDDLEWARE_CLASSES
]
