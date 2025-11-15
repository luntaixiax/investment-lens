from typing import Any
from sqlalchemy.engine import Engine
from sqlmodel import Field, SQLModel, Column, create_engine 
from sqlalchemy import ForeignKey, Boolean, JSON, ARRAY, Integer, String, Text, Date, DECIMAL, Index
from sqlalchemy_utils import EmailType, PasswordType, PhoneNumberType, ChoiceType
from sqlalchemy.exc import NoResultFound, IntegrityError
from datetime import date
from src.app.model.enums import CurType, PropertyType



def get_class_by_tablename(tablename):
    """Return class reference mapped to table.

    :param tablename: String with name of table.
    :return: Class reference or None.
    """
    for c in SQLModelWithSort._sa_registry.mappers: # type: ignore
        if hasattr(c, 'class_') and c.class_.__tablename__ == tablename:
            return c.class_

class SQLModelWithSort(SQLModel):
    
    @classmethod
    def create_table_within_collection(cls, collection: str, engine: Engine):
        # SQLModelWithSort.metadata.create_all(self.user_engine)
        # will create all tables defined across all files, even from different db
        # filter to only create tables labeled under specific collection
        for table in SQLModelWithSort.metadata.sorted_tables:
            tb_cls = get_class_by_tablename(table.name)
            if tb_cls.__collection__ == collection: # type: ignore
                table.create(bind=engine, checkfirst=True) # only create if not exist

    
    @classmethod
    def sort_for_backup(cls, rows):
        # sort rows from query, useful in case of backup
        return rows
    
    
class UserORM(SQLModelWithSort, table=True):
    __collection__: str = 'primary'
    __tablename__: str = "users"
    
    user_id: str = Field(
        sa_column=Column(
            String(length = 15), 
            primary_key = True, 
            nullable = False)
    )
    username: str = Field(
        sa_column=Column(
            String(length = 20),  
            nullable = False, 
            unique = True
        )
    )
    email: str = Field(
        sa_column=Column(
            EmailType(),  
            nullable = False, 
            unique = False
        )
    )
    hashed_password: str = Field(
        sa_column=Column(
            String(length = 72),  
            nullable = False
        )
    )
    is_admin: bool = Field(
        sa_column=Column(
            Boolean(create_constraint=True), 
            default = False, 
            nullable = False
        )
    )
    
class FxORM(SQLModelWithSort, table=True):
    __collection__: str = 'primary'
    __tablename__: str = "currency"
    
    currency: CurType = Field(
        sa_column=Column(
            ChoiceType(CurType, impl = Integer()), 
            primary_key = True, 
            nullable = False
        )
    )
    cur_dt: date = Field(
        sa_column=Column(
            Date(), 
            primary_key = True, 
            nullable = False
        )
    )
    rate: float = Field(
        sa_column=Column(
            DECIMAL(15, 5, asdecimal=False), 
            nullable = False
        )
    )
    
class PropertyORM(SQLModelWithSort, table=True):
    __collection__: str = 'primary'
    __tablename__: str = "property"
    
    __table_args__ = (
        Index(
            "ft_symbol_name_descp",  # index name
            "symbol", "name", "description",
            mysql_prefix="FULLTEXT"
        ),
    )

    
    prop_id: str = Field(
        sa_column=Column(
            String(length = 18), 
            primary_key = True, 
            nullable = False
        )
    )
    symbol: str = Field(
        sa_column=Column(
            String(length = 35), 
            primary_key = False, 
            nullable = True,
            unique = True, # TODO: only for public properties
        )
    )
    name: str = Field(
        sa_column=Column(
            String(length = 100),
            nullable = False
        )
    )
    currency: CurType = Field(
        sa_column=Column(
            ChoiceType(CurType, impl = Integer()), 
            nullable = False
        )
    )
    prop_type: PropertyType = Field(
        sa_column=Column(
            ChoiceType(PropertyType, impl = Integer()), 
            nullable = False
        )
    )
    is_public: bool = Field(
        sa_column=Column(
            Boolean(create_constraint=True), 
            default = True, 
            nullable = False
        )
    )
    description: str | None = Field(
        sa_column=Column(
            Text(),
            nullable = True
        )
    )
    custom_props: dict[str, Any] = Field(
        sa_column=Column(
            JSON(),
            nullable = True
        )
    )
    
class PrivatePropOwnershipORM(SQLModelWithSort, table=True):
    __collection__: str = 'primary'
    __tablename__: str = "private_prop_ownership"
    
    ownership_id: str = Field(
        sa_column=Column(
            String(length = 18), 
            primary_key = True, 
            nullable = False
        )
    )
    prop_id: str = Field(
        sa_column=Column(
            String(length = 18), 
            ForeignKey(
                'property.prop_id', 
                onupdate = 'CASCADE', 
                ondelete = 'RESTRICT'
            ),
            nullable = False,
            unique = True,
        )
    )
    user_id: str = Field(
        sa_column=Column(
            String(length = 15), 
            ForeignKey(
                'users.user_id', 
                onupdate = 'CASCADE', 
                ondelete = 'RESTRICT'
            ),
            nullable = False
        )
    )