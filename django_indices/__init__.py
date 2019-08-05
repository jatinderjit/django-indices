from django.db.models import options
from django_indices.json import JSONIndex

options.DEFAULT_NAMES += ('indices',)


__all__ = [JSONIndex]
