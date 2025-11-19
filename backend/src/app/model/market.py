from typing import Any, Literal
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, model_validator, computed_field
from src.app.model.enums import CurType, PropertyType
from src.app.model.registry import Property

class FxPoint(BaseModel):
    cur_dt: date = Field(
        description='The date of the property.',
    )
    rate: float = Field(
        description='The rate of the property.',
    )

class FxRate(BaseModel):
    currency: CurType = Field(
        description='The currency of the property.',
    )
    cur_dt: date = Field(
        description='The date of the property.',
    )
    rate: float = Field(
        description='The rate of the property.',
    )
    

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
    
    def to_property(self) -> Property:
        return Property(
            symbol=self.symbol,
            name=self.name or self.symbol,
            prop_type=self.prop_type,
            currency=self.currency,
            is_public=True,
            is_cash_prop=False,
            description=self.description,
            custom_props={
                'exchange': self.exchange,
                'industry': self.industry,
                'sector': self.sector,
                'country': self.country,
                'website': self.website,
            },
        )
        
    @classmethod
    def from_property(cls, property: Property) -> 'PublicPropInfo':
        return cls(
            symbol=property.symbol,
            name=property.name,
            prop_type=property.prop_type,
            currency=property.currency,
            is_cash_prop=property.is_cash_prop,
            exchange=property.custom_props.get('exchange'),
            industry=property.custom_props.get('industry'),
            sector=property.custom_props.get('sector'),
            country=property.custom_props.get('country'),
            website=property.custom_props.get('website'),
            description=property.description,
        )
    
class YFinancePricePoint(BaseModel):
    dt: date = Field(
        description='The date of the price point.',
    )
    close: float = Field(
        description='The close price, adjusted for splits.',
    )
    adj_close: float = Field(
        description='The adjusted close price, adjusted for splits and dividends.',
    )
    volume: int = Field(
        description='The volume of the price point.',
    )
    stock_splits: float = Field(
        description='The daily stock split factor, 0 for non-splitting days and > 0 for splitting days.',
    )
    dividends: float = Field(
        description='The daily dividends, 0 for non-dividend days and > 0 for dividend days.',
    )
    split_factor: float = Field(
        description='The cumulative split factor, calculated backwards from the last day to the first day.',
    )
    
    @computed_field
    def raw_close(self) -> float:
        return self.close * self.split_factor