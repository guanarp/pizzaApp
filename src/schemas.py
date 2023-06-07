from typing import List, Optional
from pydantic import BaseModel

from .models import IngredientType, UserType
"""
This is where we declare the Pydantic models, they define a Schema(valid data shape)

Notice that when we create an item(for example, pizza) we don't know the ID yet.
But when someone requests it, we''ll know

orm_mode will tell Pydantic to read data even if it's not a dict
this will let us get an atribute in two ways
var = data["attribute"] -> normal way, with a dict key
var = data.attribute -> as an orm attribute

Now, we just need to declare the response_model argument in path operations
orm_mode also helps us with lazy loading/ lazy datasets
"""


# User
class UserBase(BaseModel):
    username: str
    permission_level : UserType

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
#Notice that with separate the password, it's only there when the user is created.      


#Ingredient
class  IngredientBase(BaseModel):
    name: str
    category: IngredientType 

    class Config:
        orm_mode = True

class IngredientCreate(IngredientBase):
    pass


#Pizza
class PizzaBase(BaseModel):
    id : int
    name : str
    price : int
    #is_active : Optional[bool] = False

class Pizza(PizzaBase): #for internal use
    
    ingredients: List[IngredientBase]

    class Config:
        orm_mode = True

class PizzaList(PizzaBase): #for  /pizza
    ingredients_number: int

    class Config: 
        orm_mode = True

class PizzaDetails(PizzaBase): #for get with path {pizza_id}
    ingredients_names: Optional[list]
    is_active: bool

    class Config:
        orm_mode = True

class PizzaCreate(PizzaBase):
    is_active: bool = True
    
#Ingredients

