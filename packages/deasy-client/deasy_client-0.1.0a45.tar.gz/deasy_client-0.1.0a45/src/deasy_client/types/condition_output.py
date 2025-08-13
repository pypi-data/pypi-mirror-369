# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ConditionOutput", "Tag"]


class Tag(BaseModel):
    name: str

    values: List[Union[str, float]]

    operator: Optional[str] = None


class ConditionOutput(BaseModel):
    children: Optional[List["ConditionOutput"]] = None

    condition: Optional[Literal["AND", "OR"]] = None

    tag: Optional[Tag] = None
