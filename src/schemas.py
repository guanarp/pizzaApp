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

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    permission_level : UserType

    class Config:
        orm_mode = True
#Notice that we separate the password, it's only there when the user is created.      


#Base classes
class  IngredientBase(BaseModel):
    name: str
    category: IngredientType 

    class Config:
        orm_mode = True

class PizzaBase(BaseModel):
    id : int
    name : str
    price : int
    #is_active : Optional[bool] = False


#Pizza
class Pizza(PizzaBase):
    ingredients: List[IngredientBase]

    class Config:
        orm_mode = True

class PizzaList(PizzaBase):
    ingredients_number: int

    class Config: 
        orm_mode = True

class PizzaDetails(PizzaBase): 
    ingredients_names: Optional[list]
    is_active: bool

    class Config:
        orm_mode = True

class PizzaCreate(BaseModel): 
    #we should'nt give it the id so it inherits from BaseModel
    name: str
    price: int
    is_active: bool = True


#Ingredients
class IngredientCreate(IngredientBase):
    id : int


#Tokens
class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    
    class Config:
        orm_mode = True

class TokenPayload(BaseModel):
    sub: str 
    exp: int
    
    class Config:
        orm_mode = True




