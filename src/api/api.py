from pydantic import BaseModel, Field
from typing import Any, Dict


class MetaPayloadModel(BaseModel):
    jsonQuery: Dict[str, Any] = Field(...)

    @classmethod
    async def from_inner_dict(cls, inner: Dict[str, Any]) -> "MetaPayloadModel":
        return cls(jsonQuery=inner)

    async def to_inner_dict(self) -> Dict[str, Any]:
        return self.jsonQuery