from functools import partial
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.app.utils.tools import id_generator
from src.app.model.enums import CurType, PropertyType, PlanType

class Account(BaseModel):
    
    acct_id: str = Field(
        default_factory=partial( # type: ignore
            id_generator,
            prefix='acct-',
            length=8,
        ),
        frozen=True,
        description='The unique identifier for the account.',
    )
    acct_name: str = Field(
        description='The name/ID of the account.',
    )
    plan_type: PlanType = Field(
        description='The type of the plan.',
    )
    platform: str = Field(
        description='The platform of the account.',
    )
    
class Property(BaseModel):
    """something about the investment property itself"""
    
    prop_id: str = Field(
        default_factory=partial( # type: ignore
            id_generator,
            prefix='prop-',
            length=8,
        ),
        frozen=True,
        description='The unique identifier for the asset.',
    )
    symbol: str = Field(
        description='The ticker symbol of the property.',
    )
    name: str = Field(
        description='The name/ID of the property.',
    )
    prop_type: PropertyType = Field(
        description='The type of the property.',
    )
    currency: CurType = Field(
        description='The currency of the property.',
    ) # TODO: should it be here?