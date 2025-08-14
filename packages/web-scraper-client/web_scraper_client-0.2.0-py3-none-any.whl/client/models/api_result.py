from typing import Literal, Union, Any

from pydantic import BaseModel, Field


class ApiResult(BaseModel):
    source_type: Literal["xhr", "page_source", "nested"] = Field()
    content: Union[str, dict, list, Any] = Field()
