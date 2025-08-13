"""
This tool allows agents to interact with the Bolt API.
"""

from __future__ import annotations

from typing import Any, Optional, Type, cast

from pydantic import BaseModel

from langchain.tools import BaseTool

from ..api import BoltAPI


class BoltTool(BaseTool):
    """Tool for interacting with the Bolt API."""

    bolt_api: BoltAPI
    method: str
    name: str = ""
    description: str = ""
    args_schema: Optional[Type[BaseModel]] = None

    def _run(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Implementation of the tool."""
        method = getattr(self.bolt_api, self.method)
        return cast(str, method(*args, **kwargs))
