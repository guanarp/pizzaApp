from pydantic import BaseModel

from .models import Ingredient_type

#This is where we declare the Pydantic models, they define a Schema(valid data shape)

class PizzaBase(BaseModel):
    name : str
    price : int
    is_active : Optional[bool] = False

class  Ingredient(BaseModel):
    name: str
    type: Ingredient_type 
    