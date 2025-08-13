"""
Contains descriptions and default values for settings that are used by the zeromigrations command.
The settings can be overridden in the django settings file by prefixing the names with `ZERO_MIGRATIONS_`.
"""

from typing import Callable, Optional

from django.conf import settings

APPS: Optional[list[str]] = getattr(settings, "ZERO_MIGRATIONS_APPS", None)
"""The apps to reset migrations for. default: `None`. Will reset migrations for all local apps if `None`."""

ALLOW_CREATE_DEBUG_FALSE: bool = getattr(
    settings, "ZERO_MIGRATIONS_ALLOW_CREATE_DEBUG_FALSE", False
)
"""Whether the create action can be run in `DEBUG = False` mode. default: `False`"""

CONFIRM_CREATE_DEBUG_FALSE: bool = getattr(
    settings, "ZERO_MIGRATIONS_CONFIRM_CREATE_DEBUG_FALSE", False
)
"""Whether to ask for confirmation before running the create action in `DEBUG = False` mode. default: `False`"""

ALLOW_APPLY_DEBUG_FALSE: bool = getattr(
    settings, "ZERO_MIGRATIONS_ALLOW_APPLY_DEBUG_FALSE", True
)
"""Whether the apply action can be run in `DEBUG = False` mode. default: `True`"""

CONFIRM_APPLY_DEBUG_FALSE: bool = getattr(
    settings, "ZERO_MIGRATIONS_CONFIRM_APPLY_DEBUG_FALSE", True
)
"""Whether to ask for confirmation before running the apply action in `DEBUG = False` mode. default: `True`"""

BEFORE_CREATE_HOOK: Optional[Callable[[], None]] = getattr(
    settings, "ZERO_MIGRATIONS_BEFORE_CREATE_HOOK", None
)
"""The hook to run before creating new migrations. default: `None`."""
