from functools import lru_cache
from django.utils.module_loading import import_string


@lru_cache
def cached_import_string(path: str):
    return import_string(path)
