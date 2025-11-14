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
    user_id: str = Field(
        description='The ID of the user the account belongs to.',
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
    is_public: bool = Field(
        default=True,
        description='Whether the property is public to all users or only the owner, e.g., real estate, etc.',
    )
    description: str | None = Field(
        description='The description of the property.',
    )
    
    @model_validator(mode='after')
    def check_is_public(self) -> 'Property':
        # these asset belongs to the owner only, and is unique to the owner
        if self.prop_type in [PropertyType.REAL_ESTATE, PropertyType.DEBT]:
            self.is_public = False
        return self
    
    
class PrivatePropOwnership(BaseModel):
    """ all properties that are not public should be owned by a user, and registered in this model """
    
    ownership_id: str = Field(
        default_factory=partial( # type: ignore
            id_generator,
            prefix='own-',
            length=8,
        ),
        frozen=True,
        description='The unique identifier for the ownership.',
    )
    prop_id: str = Field(
        description='The ID of the property the ownership belongs to.',
    )
    user_id: str = Field(
        description='The ID of the user the ownership belongs to.',
    )