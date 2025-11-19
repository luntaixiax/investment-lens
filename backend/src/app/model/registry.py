from functools import partial
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.app.utils.tools import id_generator
from src.app.model.enums import CurType, PropertyType, PlanType, EstateType, \
    BusinessType, UnderlyingType, RiskLevel, LiquidityType

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
    is_cash_prop: bool = Field(
        default=False,
        description='Whether the property is a cash property. (counter accout for non-cash property transactions)',
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
    custom_props: dict[str, Any] = Field(
        description='Custom properties of the property.',
    )
    
    @model_validator(mode='after')
    def check_is_public(self) -> 'Property':
        # these asset belongs to the owner only, and is unique to the owner
        if self.prop_type in [PropertyType.REAL_ESTATE, PropertyType.DEBT]:
            self.is_public = False
        return self
    
    @model_validator(mode='after')
    def check_is_cash_prop(self) -> 'Property':
        if self.is_cash_prop:
            if self.prop_type != PropertyType.CASH:
                raise ValueError('Cash property must be of type CASH')
            if not self.is_public:
                raise ValueError('Cash property must be public')
            if self.symbol != self.currency.name:
                raise ValueError('Cash property symbol must be the same as the currency name')
        else:
            if self.prop_type == PropertyType.CASH:
                raise ValueError('Non-cash property cannot be of type CASH')
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
    
class RealEstateProperty(BaseModel):
    """ real estate property, not persist directly in the database """
    
    name: str = Field(
        description='The nickname of the real estate property.',
    )
    address: str = Field(
        description='The address of the real estate property.',
    )
    country: str = Field(
        description='The country of the real estate property.',
    )
    currency: CurType = Field(
        description='The currency of the real estate property.',
    )
    estate_type: EstateType = Field(
        description='The type of the real estate property.',
    )
    size: float = Field(
        description='The size of the real estate property. (in square feet)',
    )
    year_built: int = Field(
        description='The year the real estate property was built.',
    )
    description: str | None = Field(
        description='The description of the property.',
    )
    
    def to_property(self) -> Property:
        return Property(
            symbol=id_generator(prefix='real-', length=8),
            name=self.name,
            prop_type=PropertyType.REAL_ESTATE,
            currency=self.currency,
            is_public=False,
            description=self.description or f"{self.estate_type} in {self.address}",
            custom_props={
                'address': self.address,
                'country': self.country,
                'estate_type': self.estate_type,
                'size': self.size,
                'year_built': self.year_built,
            },
        )
        
class BusinessProperty(BaseModel):
    """ business property, not persist directly in the database """
    
    name: str = Field(
        description='The nickname of the business.',
    )
    address: str = Field(
        description='The address of the business.',
    )
    country: str = Field(
        description='The country of the business.',
    )
    business_type: BusinessType = Field(
        description='The type of the business.',
    )
    currency: CurType = Field(
        description='The currency of the business.',
    )
    year_founded: int = Field(
        description='The year the business was founded.',
    )
    description: str | None = Field(
        description='The description of the business.',
    )
    
    
    def to_property(self) -> Property:
        return Property(
            symbol=id_generator(prefix='biz-', length=8),
            name=self.name,
            prop_type=PropertyType.BUSINESS,
            currency=self.currency,
            is_public=False,
            description=self.description or f"{self.name} ({self.business_type})",
            custom_props={
                'address': self.address,
                'country': self.country,
                'business_type': self.business_type,
                'year_founded': self.year_founded,
            },
        )
        
class PrivateFundProperty(BaseModel):
    """ private fund property, not persist directly in the database """
    
    name: str = Field(
        description='The nickname of the private fund.',
    )
    currency: CurType = Field(
        description='The currency of the private fund.',
    )
    management: str = Field(
        description='The management company of the private fund.',
    )
    underlying: UnderlyingType = Field(
        description='The underlying assets of the private fund.',
    )
    risk_level: RiskLevel = Field(
        description='The risk level of the private fund.',
    )
    liquidity: LiquidityType = Field(
        description='The liquidity of the private fund.',
    )
    description: str | None = Field(
        description='The description of the private fund.',
    )
    
    def to_property(self) -> Property:
        return Property(
            symbol=id_generator(prefix='fund-', length=8),
            name=self.name,
            prop_type=PropertyType.FUND_PRIV,
            currency=self.currency,
            is_public=False,
            description=self.description or f"{self.name} ({self.management})",
            custom_props={
                'management': self.management,
                'underlying': self.underlying,
                'risk_level': self.risk_level,
                'liquidity': self.liquidity,
            },
        )
        
class DebtProperty(BaseModel):
    """ debt property, not persist directly in the database """
    
    name: str = Field(
        description='The nickname of the debt.',
    )
    currency: CurType = Field(
        description='The currency of the debt.',
    )
    borrower: str = Field(
        description='The borrower of the debt.',
    )
    risk_level: RiskLevel = Field(
        description='The risk level of the debt.',
    )
    description: str | None = Field(
        description='The description of the debt.',
    )
    
    def to_property(self) -> Property:
        return Property(
            symbol=id_generator(prefix='debt-', length=8),
            name=self.name,
            prop_type=PropertyType.DEBT,
            currency=self.currency,
            is_public=False,
            description=self.description or f"Private debt to {self.borrower}",
            custom_props={
                'borrower': self.borrower,
                'risk_level': self.risk_level,
            },
        )