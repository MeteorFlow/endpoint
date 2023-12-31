from typing import List, Optional

from pydantic import Field

from meteor.models import MeteorBase


# Pydantic models...
class SearchBase(MeteorBase):
    query: Optional[str] = Field(None, nullable=True)


class SearchRequest(SearchBase):
    pass


class ContentResponse(MeteorBase):
    class Config:
        allow_population_by_field_name = True


class SearchResponse(MeteorBase):
    query: Optional[str] = Field(None, nullable=True)
    results: ContentResponse
