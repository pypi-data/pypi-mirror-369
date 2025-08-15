# (C) 2021 Arturo Borrero Gonzalez <aborrero@wikimedia.org>
# (C) 2022 Taavi Väänänen <hi@taavi.wtf>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#

from logging import getLogger
from typing import Any, Dict, Optional

import requests
from toolforge_weld.errors import ToolforgeError, ToolforgeUserError

LOGGER = getLogger(__name__)


class TjfCliError(ToolforgeError):
    """Raised when an HTTP request fails."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)

        if context:
            # property is defined in parent class
            self.context = context


class TjfCliUserError(TjfCliError, ToolforgeUserError):
    """Raised when an HTTP request fails with a 4xx status code."""


def handle_http_exception(e: requests.exceptions.HTTPError) -> Exception:
    if e.response is None:
        return TjfCliError(message="Got no response", context={})

    message = e.response.text
    context = {}
    try:
        data = e.response.json()
        if isinstance(data, dict):
            if "error" in data:
                message = "\n".join(data["error"])
                context = {"messages": data}
        elif isinstance(data, str):
            message = data
    except requests.exceptions.InvalidJSONError:
        pass

    if 400 <= e.response.status_code <= 499:
        return TjfCliUserError(message=message, context=context)
    else:
        return TjfCliError(message=message, context=context)


def handle_connection_error(e: ConnectionError) -> Exception:
    context = {}
    if isinstance(e, requests.exceptions.HTTPError):
        context["body"] = e.response.text if e.response is not None else ""

    return TjfCliError(
        message="The jobs service seems to be down – please retry in a few minutes.",
        context=context,
    )
