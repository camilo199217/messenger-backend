from typing import Literal, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: Optional[int] = Field(1, ge=1)
    size: Optional[int] = Field(10, ge=0, le=100)
    search: Optional[str] = Field(None, max_length=100)
    descending: Optional[Literal["ASC", "DESC"]] = Field("ASC")
    sort_by: Optional[str] = Field(None, max_length=50)
