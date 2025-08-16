from typing import (
    Optional,
)

from pjdev_sqlmodel.models.settings_models import TSettings


class Context:
    settings: Optional[TSettings] = None


__ctx = Context()


def init_settings(settings: TSettings) -> None:
    __ctx.settings = settings


def get_settings() -> TSettings:
    if __ctx.settings is None:
        msg = "Settings are not initialized -- call init_settings()"
        raise Exception(msg)
    return __ctx.settings
