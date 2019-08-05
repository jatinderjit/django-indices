from django.db.models import options
from json_index.index import JsonIndex

options.DEFAULT_NAMES += ('json_indices',)


__all__ = [JsonIndex]
