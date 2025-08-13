# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, TypedDict

__all__ = ["SchemaUpsertParams"]


class SchemaUpsertParams(TypedDict, total=False):
    schema_name: Required[str]

    new_schema_name: Optional[str]

    schema_data: Optional[Dict[str, object]]

    schema_description: Optional[str]
