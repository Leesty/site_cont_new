"""Хранилище медиа: S3 из настроек в БД или локальный каталог."""
import time

from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Кэш конфига из БД (ключ, чтобы сбросить при сохранении в админке)
_MEDIA_CONFIG_CACHE = {"config": None, "cache_until": 0}
CACHE_SECONDS = 300


def get_media_config_from_db():
    """Возвращает единственную запись MediaStorageConfig из БД (с кэшем)."""
    now = time.time()
    if _MEDIA_CONFIG_CACHE["config"] is not None and now < _MEDIA_CONFIG_CACHE["cache_until"]:
        return _MEDIA_CONFIG_CACHE["config"]
    try:
        from .models import MediaStorageConfig
        config = MediaStorageConfig.objects.filter(enabled=True).first()
        if not config or not config.bucket_name or not config.access_key_id or not config.secret_access_key:
            config = None
        _MEDIA_CONFIG_CACHE["config"] = config
        _MEDIA_CONFIG_CACHE["cache_until"] = now + CACHE_SECONDS
        return config
    except Exception:
        return None


def clear_media_config_cache():
    """Сбросить кэш (вызвать после сохранения настроек в админке)."""
    _MEDIA_CONFIG_CACHE["config"] = None
    _MEDIA_CONFIG_CACHE["cache_until"] = 0


class ConfigurableMediaStorage(FileSystemStorage):
    """Storage, который при первом обращении выбирает бэкенд: S3 из БД или локальный каталог."""

    def __init__(self, **kwargs):
        # Инициализируем как FileSystemStorage по умолчанию (location из settings)
        super().__init__(location=kwargs.get("location", settings.MEDIA_ROOT), **kwargs)
        self._s3_backend = None
        self._use_s3 = None

    def _resolve_backend(self):
        if self._use_s3 is not None:
            return self._s3_backend if self._use_s3 else self
        config = get_media_config_from_db()
        if config and config.enabled and config.bucket_name and config.access_key_id and config.secret_access_key:
            try:
                from storages.backends.s3boto3 import S3Boto3Storage
                opts = {
                    "access_key": config.access_key_id,
                    "secret_key": config.secret_access_key,
                    "bucket_name": config.bucket_name,
                    "region_name": config.region_name or "ru-1",
                }
                if config.endpoint_url:
                    opts["endpoint_url"] = config.endpoint_url
                self._s3_backend = S3Boto3Storage(**opts)
                self._use_s3 = True
                return self._s3_backend
            except Exception:
                pass
        self._use_s3 = False
        return self

    def _open(self, name, mode="rb"):
        backend = self._resolve_backend()
        if backend is self:
            return super()._open(name, mode)
        return backend._open(name, mode)

    def _save(self, name, content):
        backend = self._resolve_backend()
        if backend is self:
            return super()._save(name, content)
        return backend._save(name, content)

    def delete(self, name):
        backend = self._resolve_backend()
        if backend is self:
            return super().delete(name)
        return backend.delete(name)

    def exists(self, name):
        backend = self._resolve_backend()
        if backend is self:
            return super().exists(name)
        return backend.exists(name)

    def url(self, name):
        backend = self._resolve_backend()
        if backend is self:
            return super().url(name)
        return backend.url(name)

    def path(self, name):
        backend = self._resolve_backend()
        if backend is self:
            return super().path(name)
        if hasattr(backend, "path"):
            return backend.path(name)
        return None  # S3 — нет локального пути
