from functools import lru_cache
from pathlib import Path

import yaml

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"

SUPPORTED_LANGS = ("en", "ru", "uk")


@lru_cache(maxsize=8)
def _load_locale(locale: str) -> dict:
    file = LOCALES_DIR / f"{locale}.yaml"
    if not file.exists():
        file = LOCALES_DIR / "en.yaml"
    with open(file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def t(key: str, locale: str = "en") -> str:
    if locale not in SUPPORTED_LANGS:
        locale = "en"
    data = _load_locale(locale)
    return data.get(key, key)
