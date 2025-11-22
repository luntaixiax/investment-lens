from functools import partial
from typing import Any, Literal
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, model_validator, computed_field
from src.app.utils.tools import id_generator
from src.app.model.enums import CurType, PropertyType, PlanType, LegType


class LegCreate(BaseModel):

    leg_type: LegType = Field(
        description='The type of the transaction leg.',
    )
    acct_id: str = Field(
        description='The ID of the account the transaction belongs to.',
    )
    prop_id: str = Field(
        description='The ID of the property the transaction belongs to.',
    )
    quantity: float = Field(
        description='The quantity of the transaction.',
    )
    price: float = Field(
        description='The price of the transaction.',
    )
    
    @computed_field
    @property
    def amount(self) -> float:
        return round(self.quantity * self.price, 2)
    
    @computed_field
    @property
    def cf_direction(self) -> int:
        if self.leg_type in [LegType.SELL, LegType.INTEREST, LegType.DIVIDEND, LegType.RENT]:
            return 1
        elif self.leg_type in [LegType.BUY, LegType.FEE, LegType.TAX]:
            return -1
        else: # OTHER
            return 0

    
class Leg(LegCreate):
    
    leg_id: str = Field(
        default_factory=partial( # type: ignore
            id_generator,
            prefix='leg-',
            length=8,
        ),
        frozen=True,
        description='The unique identifier for the transaction leg.',
    )
    trans_id: str = Field(
        description='The ID of the transaction the transaction leg belongs to.',
    )
    user_id: str = Field(
        description='The ID of the user the transaction leg belongs to.',
    )

        
class TransactionWOLegs(BaseModel):
    trans_id: str = Field(
        default_factory=partial( # type: ignore
            id_generator,
            prefix='trans-',
            length=8,
        ),
        frozen=True,
        description='The unique identifier for the transaction.',
    )
    user_id: str = Field(
        description='The ID of the user the transaction belongs to.',
    )
    trans_dt: date = Field(
        description='The date of the transaction.',
    )
    description: str = Field(
        description='The description of the transaction.',
    )
    
class TransactionCreate(TransactionWOLegs):

    legs: list[LegCreate] = Field(
        description='The legs of the transaction.',
    )
    
    def to_transaction_wolgs(self) -> TransactionWOLegs:
        return TransactionWOLegs(
            **self.model_dump(exclude={'legs'})
        )
    
    
class Transaction(TransactionWOLegs):

    legs: list[Leg] = Field(
        description='The legs of the transaction.',
    )
    


    @model_validator(mode='after')
    def check_legs(self) -> 'Transaction':
        for leg in self.legs:
            if leg.trans_id != self.trans_id:
                raise ValueError('Leg transaction ID must be the same as the transaction ID.')
        return self
    
    @model_validator(mode='after')
    def check_user_id(self) -> 'Transaction':
        for leg in self.legs:
            if leg.user_id != self.user_id:
                raise ValueError(f'Leg user ID {leg.user_id} must be the same as the transaction user ID {self.user_id}.')
        return self