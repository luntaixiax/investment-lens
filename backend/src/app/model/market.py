from typing import Any, Literal
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, model_validator, computed_field
from src.app.model.enums import CurType, PropertyType

class PublicPropInfo(BaseModel):
    
    symbol: str = Field(
        description='The ticker symbol of the property.',
    )
    name: str | None = Field(
        description='The long name/ID of the property.',
    )
    exchange: str | None = Field(
        description='The exchange of the property.',
    )
    currency: CurType = Field(
        description='The currency of the property.',
    )
    prop_type: PropertyType = Field(
        description='The type of the instrument.',
    )
    industry: str | None = Field(
        description='The industry of the property.',
    )
    sector: str | None = Field(
        description='The sector of the property.',
    )
    country: str | None = Field(
        description='The country of the property.',
    )
    website: str | None = Field(
        description='The website of the property.',
    )
    description: str | None = Field(
        description='The summary of the property.',
    )