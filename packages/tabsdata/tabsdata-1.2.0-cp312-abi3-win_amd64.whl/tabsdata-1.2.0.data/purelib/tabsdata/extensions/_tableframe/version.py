#
# Copyright 2025 Tabs Data Inc.
#

import importlib.metadata

from tabsdata._utils.constants import TABSDATA_MODULE_NAME


def version() -> str:
    # noinspection PyBroadException
    try:
        return importlib.metadata.version(TABSDATA_MODULE_NAME)
    except Exception:
        return "Unknown"
