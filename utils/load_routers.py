import importlib
from pathlib import Path

from aiogram import Router

HANDLERS_DIR = Path(__file__).resolve().parent.parent / "bot"
EXCLUDED = {"catch_all"}


def load_routers() -> Router:
    main_router = Router()

    for handler_file in sorted(HANDLERS_DIR.rglob("handlers.py")):
        relative = handler_file.relative_to(HANDLERS_DIR)
        module_name = relative.parts[0]

        if module_name in EXCLUDED:
            continue

        module_path = f"bot.{'.'.join(relative.with_suffix('').parts)}"

        module = importlib.import_module(module_path)
        if hasattr(module, "router"):
            main_router.include_router(module.router)

    return main_router
