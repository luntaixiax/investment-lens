from functools import partial
from typing import Any, Literal
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, model_validator, computed_field
from src.app.utils.tools import id_generator
from src.app.model.enums import CurType, PropertyType, PlanType, TransactionType


class Transaction(BaseModel):
    
    trans_id: str = Field(
        default_factory=partial( # type: ignore
            id_generator,
            prefix='trans-',
            length=8,
        ),
        frozen=True,
        description='The unique identifier for the transaction.',
    )
    trans_type: TransactionType = Field(
        description='The type of the transaction.',
    )
    trans_dt: date = Field(
        description='The date of the transaction.',
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