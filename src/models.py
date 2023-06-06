import enum

from typing import Optional

from pydantic import BaseModel

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base


#Enum
## This is to add other categories in the future

class IngredientType(enum.Enum): 
    basic = "basic"
    premium = "premium"

class UserType(enum.Enum):
    basic = "basic"
    staff = "staff"
    SU = "SU"


pizza_ingredient_association = Table(
    'pizza_ingredient', Base.metadata,
    Column('pizza_id', Integer, ForeignKey('pizzas.id')),
    Column('ingredient_id',Integer, ForeignKey('ingredients.id')))

#SQLAlchemy models

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String) #this is actually hashed
    is_active = Column(Boolean, default=True)
    permission_level = Column(Enum(UserType),default=UserType.basic)

    #items = relationship("Item", back_populates="owner")

class Pizza(Base):
    __tablename__ = "pizzas"

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, index = True)
    price = Column(Integer, index = True)
    is_active = Column(Boolean, default = False)
    
    ingredients = relationship(
        "Ingredient", secondary = pizza_ingredient_association, 
        back_populates="pizzas")
    #ingredients_number = len(ingredients)

    #def get_ingredients_number(self): #verificar si necesito la funcion
    #    return len(self.ingredients)


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String, index=True)
    category = Column(Enum(IngredientType), default=IngredientType.basic) #verificar si necesito index = true

    pizzas = relationship(
        "Pizza", secondary = pizza_ingredient_association, 
        back_populates = "ingredients")
    
