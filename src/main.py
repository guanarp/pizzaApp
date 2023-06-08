from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import (
    OAuth2PasswordRequestForm, HTTPBasic, 
    HTTPBasicCredentials
)
from sqlalchemy.orm import Session

from base64 import b64encode

from . import CRUD, models, schemas
from .database import SessionLocal, engine, get_db
from .deps import get_current_user
from .utils import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password
)


models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)

security = HTTPBasic()


#CurrentUser = Annotated[User, Depends(get_current_user)]        

@app.get("/")
def home() -> dict:
    """
    Home endpoint to welcome users to the pizza app.

    Returns:
    - Welcome dictionary
    """
    return {"Welcome": "to the pizza app"}

#Users
@app.post("/signup", summary="Create new user", response_model=schemas.User)
async def create_user(data: schemas.UserCreate, db: Session = Depends(get_db)) -> models.User:
    """
    Endpoint for creating a new user.

    Parameters:
    - data: User creation data.
    - db: Database session dependency.

    Returns:
    - The created user model.
    """
    user = CRUD.get_user_by_username(db,data.username)
    #querying database to check if user already exist
    if user is None:
        return CRUD.create_user(db, data)
    raise HTTPException(status_code=400, detail = "The username already exists")

@app.post("/login", response_model=schemas.TokenSchema)
async def login(
    form_data: OAuth2PasswordRequestForm=Depends(), db : Session=Depends(get_db)) -> dict:
    """
    Endpoint for JWT authentication login.

    Parameters:
    - form_data: OAuth2PasswordRequestForm containing the provided username and password.
    - db: Database session dependency.

    Returns:
    - Token response containing the access token and refresh token.
    """
    user = CRUD.get_user_by_username(db,form_data.username)
    if user is None:
        raise HTTPException(status_code=400, detail = "Incorrect username or password")
    print(user.password)
    hashed_password = user.password
    if verify_password(form_data.password, hashed_password):
        return {
            "access_token": create_access_token(user.username),
            "refresh_token": create_refresh_token(user.username)
        }
    raise HTTPException(status_code=400, detail = "Incorrect username or password")

@app.post("/login/basic")
def login_basic(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Endpoint for basic authentication login.

    Parameters:
    - credentials: HTTPBasicCredentials object containing the provided username and password.

    Returns:
    - Token response containing the access token.

    Raises:
    - HTTPException 401: If the provided credentials are invalid.
    """
    if credentials.username == "admin" and credentials.password == "tdp":
        #in a real exmample the user and password should be hashed or in .env variables
        #also, the user can be looked up in users db filtering non basic users instead of #doing "== admin"

        token = b64encode(f"{credentials.username}:{credentials.password}".encode("utf-8")).decode("utf-8")
        return {"token_type": "basic", "access_token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.patch("/user/{user_id}", response_model = schemas.User)
def modify_user_permission(
    user_id: int, level, db: Session = Depends(get_db), 
    modifier: models.User = Depends(get_current_user)) -> models.User:
    """
    Endpoint to modify the permission level of a user.

    Parameters:
    - user_id: The ID of the user to modify.
    - level: The new permission level to assign.
    - db: Database session dependency.
    - modifier: The currently authenticated user making the modification.

    Returns:
    - The updated user model.
    """
    if modifier.permission_level != models.UserType.SU:
        raise HTTPException(status_code=403, detail="You must be a SU to modify users")
    user_db = CRUD.get_user(db, user_id) 
    if user_db is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_db = CRUD.modify_user_permission(db, user_db, level)

    return user_db
    




#Pizza CRUD
@app.get("/pizzas", response_model=List[schemas.PizzaList])
def show_pizzas(
        db: Session = Depends(get_db), 
        user: models.User = Depends(get_current_user))-> List[schemas.PizzaList]:
    """
    Endpoint to retrieve a list of pizzas.
    - Regular users get only active pizzas.
    - Staff/SU gets all pizzas.

    Parameters:
    - db: Database session dependency.

    Returns:
    - List of pizzas according to user type

    """
    get_all = False
    if user.permission_level != models.UserType.basic:
        get_all = True
    pizza_list = CRUD.get_pizza_list(db,get_all)
    for pizza in pizza_list:
        pizza.ingredient_number = len(pizza.ingredients)
    return pizza_list

@app.get("/pizzas/{pizza_id}", response_model = schemas.PizzaDetails)
def show_pizza_details(
    pizza_id: int, db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user)) -> schemas.PizzaDetails:
    """
    Endpoint to retrieve details of a specific pizza by ID.
    
    Parameters:
    - pizza_id: The ID of the pizza to retrieve.
    - db: Database session dependency.

    Returns:
    - Details of the pizza.
    """
    if user.permission_level == models.UserType.basic:
        raise HTTPException(
            status_code=403, detail="You must be a staff or higher to see details")

    pizza_detail = CRUD.get_pizza(db, pizza_id)
    
    if pizza_detail is None:
        raise HTTPException(status_code=404, detail = "Pizza not found")
    
    return pizza_detail

@app.post("/pizzas/",response_model = schemas.Pizza)
def create_pizza(
    new_pizza: schemas.PizzaCreate, db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user)) -> schemas.Pizza:
    """
    Endpoint to create a new pizza.

    Parameters:
    - new_pizza: The details of the new pizza to create.
    - db: Database session dependency.

    Returns:
    - The created pizza.
    """
    if user.permission_level == models.UserType.basic:
        raise HTTPException(status_code=403, 
                            detail="You must be a staff or higher to create pizzas")
    
    return CRUD.create_pizza(db, new_pizza)

@app.patch("/pizzas/{pizza_id}", response_model = schemas.PizzaDetails)
def change_pizza(
    pizza_id: int, name: str | None = None, price: int | None = None, 
    is_active: bool | None = None, db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user)) -> schemas.PizzaDetails:
    """
    Endpoint to update the details of a pizza.

    Parameters:
    - pizza_id: The ID of the pizza to update.
    - name: The new name of the pizza (optional).
    - price: The new price of the pizza (optional).
    - is_active: The new active status of the pizza (optional).
    - db: Database session dependency.

    Returns:
    - The updated pizza details.
    """
    if user.permission_level == models.UserType.basic:
        raise HTTPException(
            status_code=403, detail="You must be a staff or higher to modify pizzas")


    pizza_detail = CRUD.get_pizza(db, pizza_id)
    if pizza_detail is None:
        raise HTTPException(status_code=404, detail="Pizza not found.")
    pizza_detail = CRUD.change_pizza(db, pizza_detail, name, price, is_active)
    return pizza_detail


#Ingredient CRUD
@app.post("/ingredients", response_model = schemas.IngredientCreate)
def create_ingredient(
    new_ingredient: schemas.IngredientBase, db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user)) -> schemas.IngredientCreate:
    """
    Endpoint to create a new ingredient

    Parameters:
    - new_ingredient: The details of the new ingredient to create.
    - db: Database session dependency.

    Returns:
    - The created ingredient.
    """
    if user.permission_level == models.UserType.basic:
        raise HTTPException(
            status_code=403, detail="You must be a staff or higher to create ingredients")
    
    return CRUD.create_ingredient(db,new_ingredient)

@app.patch("/ingredients/{ingredient_id}",response_model = schemas.IngredientBase)
def change_ingredient(
    ingredient_id: int, name: str | None = None, category: str | None = None, 
    db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user)) -> schemas.IngredientBase:
    """
    Endpoint to update the details of an ingredient.

    Parameters:
    - ingredient_id: The ID of the ingredient to update.
    - name: The new name of the ingredient (optional).
    - category: The new category of the ingredient (optional).
    - db: Database session dependency.

    Returns:
    - The updated ingredient details.
    """
    if user.permission_level == models.UserType.basic:
        raise HTTPException(
            status_code=403, detail="You must be a staff or higher to modify ingredients")

    ingredient = CRUD.get_ingredient(db,ingredient_id)
    if ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found.")
    ingredient = CRUD.change_ingredient(db, ingredient, name, category)
    return ingredient
    
@app.delete("/ingredients/{ingredient_id}")
def delete_ingredient(
    ingredient_id: int, db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user)) -> dict: 
    """
    Endpoint to delete an ingredient.

    Parameters:
    - ingredient_id: The ID of the ingredient to delete.
    - db: Database session dependency.

    Returns:
    - Status of the deletion.
    """
    if user.permission_level == models.UserType.basic:
        raise HTTPException(
            status_code=403, detail="You must be a staff or higher to delete ingredients")

    ingredient = CRUD.get_ingredient(db, ingredient_id)
    if ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found.")
    deleted = CRUD.delete_ingredient(db,ingredient)
    if deleted:
        return {
            "status" : "completed", 
            "detail" : f"Ingredient {ingredient.name} with id {ingredient.id} deleted"
        }
    
    raise HTTPException (status_code=400, detail="Cannot delete an ingredient in an active pizza")

#Pizza-ingredient association
@app.post("/pizzas/ingredients/{pizza_id}/{ingredient_id}")
def add_ingredient_to_pizza(
    pizza_id : int, ingredient_id: int, db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user)):
    """
    Endpoint to add an ingredient to a pizza.

    Parameters:
    - pizza_id: The ID of the pizza.
    - ingredient_id: The ID of the ingredient to add.
    - db: Database session dependency.

    Returns:
    - The created association between the pizza and ingredient.
    """
    if user.permission_level == models.UserType.basic:
        raise HTTPException(
            status_code=403, 
            detail="You must be a staff or higher to add ingredients to pizzas")

    if CRUD.get_pizza(db, pizza_id) is None:
        raise HTTPException(status_code=404, detail=f"Pizza not found")

    if CRUD.get_ingredient(db, ingredient_id) is None:
        raise HTTPException(status_code=404, detail=f"Ingredient not found")

    association = CRUD.get_pizza_ing_association(db, pizza_id, ingredient_id)
    if association:
        raise HTTPException(status_code=400, detail="Association already exists")
    new_association = CRUD.add_pizza_ing_association(db, pizza_id, ingredient_id)
    print(new_association)
    return new_association

@app.delete("/pizzas/ingredients/{pizza_id}/{ingredient_id}")
def remove_ingredient_to_pizza(
    pizza_id : int, ingredient_id: int, db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user)) -> dict:
    """
    Endpoint to remove an ingredient from a pizza.

    Parameters:
    - pizza_id: The ID of the pizza.
    - ingredient_id: The ID of the ingredient to remove.
    - db: Database session dependency.

    Returns:
    - Status of the removal.
    """
    if user.permission_level == models.UserType.basic:
        raise HTTPException(
            status_code=403, 
            detail="You must be a staff or higher to delete ingredients from pizzas")
    
    association = CRUD.get_pizza_ing_association(db, pizza_id, ingredient_id)

    if not(association):
        raise HTTPException(status_code=404, detail="Association not found")
    CRUD.delete_pizza_ing_association(db, association)
    return {
        "status" : "completed", 
        "detail" : f"Ingredient {association.ingredient_id} "
                    f"removed from pizza {association.pizza_id}"
    }


    