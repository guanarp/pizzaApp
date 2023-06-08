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


class PizzaIngredientAssociation(Base): 
    __tablename__ = 'pizza_ingredient_association'
    pizza_id = Column(ForeignKey("pizzas.id"), primary_key=True)
    ingredient_id = Column(ForeignKey("ingredients.id"), primary_key=True)

    ingredient = relationship("Ingredient", back_populates="pizzas")
    pizza = relationship("Pizza", back_populates="ingredients")



#SQLAlchemy models

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String) #this is actually hashed
    is_active = Column(Boolean, default=True)
    permission_level = Column(Enum(UserType),default=UserType.basic)

    

class Pizza(Base):
    __tablename__ = "pizzas"

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, unique = True, index = True)
    price = Column(Integer, index = True)
    is_active = Column(Boolean, default = False)
    
    ingredients = relationship(
        "PizzaIngredientAssociation", 
        back_populates="pizza")

    @property
    def ingredients_number(self):
        return len(self.ingredients)



class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String, unique=True, index=True)
    category = Column(Enum(IngredientType), default=IngredientType.basic) #verificar si necesito index = true


    pizzas = relationship(
        "PizzaIngredientAssociation", 
        back_populates = "ingredient")
    
