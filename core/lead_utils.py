"""Вспомогательные функции для лидов: автоопределение типа базы, сжатие скриншотов."""
from __future__ import annotations

import io
from typing import TYPE_CHECKING

from django.db.models import Q

if TYPE_CHECKING:
    from .models import User

from .models import BaseType, Contact


def determine_base_type_for_contact(raw_contact: str, user: User) -> BaseType | None:
    """Определяет тип базы по контакту: по URL или по наличию в выданных/общих базах (как в боте)."""
    if not raw_contact or not raw_contact.strip():
        return None
    contact_lower = raw_contact.strip().lower()

    # По URL — только те типы, которые есть в BaseType
    if "instagram.com" in contact_lower:
        return BaseType.objects.filter(slug="instagram").first()
    if "vk.com" in contact_lower or "vk.ru" in contact_lower:
        return BaseType.objects.filter(slug="vk").first()
    if "ok.ru" in contact_lower:
        return BaseType.objects.filter(slug="ok").first()
    if "t.me" in contact_lower or contact_lower.startswith("@"):
        return BaseType.objects.filter(slug="telegram").first()
    # avito, yula, kwork — нет в BaseType, не подставляем

    # По базе контактов: сначала выданные пользователю, потом вся база
    value_clean = raw_contact.strip()
    contact = (
        Contact.objects.filter(
            Q(value__iexact=value_clean) | Q(value=value_clean),
            assigned_to=user,
        )
        .select_related("base_type")
        .first()
    )
    if contact:
        return contact.base_type
    contact = (
        Contact.objects.filter(
            Q(value__iexact=value_clean) | Q(value=value_clean),
        )
        .select_related("base_type")
        .first()
    )
    if contact:
        return contact.base_type
    return None


def compress_lead_attachment(lead) -> bool:
    """Сжимает файл вложения лида, если это изображение. Перезаписывает файл на месте."""
    if not lead or not getattr(lead, "attachment", None) or not lead.attachment:
        return False
    try:
        from PIL import Image
    except ImportError:
        return False

    path = getattr(lead.attachment, "path", None)
    if not path:
        return False
    try:
        with Image.open(path) as img:
            if img.format not in ("JPEG", "PNG", "GIF", "WEBP"):
                return False
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            elif img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            max_side = 1600
            w, h = img.size
            if w > max_side or h > max_side:
                if w >= h:
                    new_w, new_h = max_side, int(h * max_side / w)
                else:
                    new_w, new_h = int(w * max_side / h), max_side
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=82, optimize=True)
            buf.seek(0)
        with open(path, "wb") as f:
            f.write(buf.getvalue())
        return True
    except Exception:
        return False
