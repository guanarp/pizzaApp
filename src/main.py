from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from . import CRUD, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)


def get_db() -> Session:
    """
    Dependency function to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#CurrentUser = Annotated[User, Depends(get_current_user)]        

@app.get("/")
def home() -> dict:
    """
    Home endpoint to welcome users to the pizza app.

    Returns:
    - Welcome dictionary
    """
    return {"Welcome": "to the pizza app"}


#Pizza CRUD
@app.get("/pizzas", response_model=List[schemas.PizzaList])
def show_pizzas(db: Session = Depends(get_db)
                ) -> List[schemas.PizzaList]: #user: models.User = Depends(get_current_user)
    """
    Endpoint to retrieve a list of pizzas.
    - Regular users get only active pizzas.
    - Staff/SU gets all pizzas.

    Parameters:
    - db: Database session dependency.

    Returns:
    - List of pizzas according to user type

    """
    get_all = True
    #if user.permission_level != 1:
    #    get_all = True
    pizza_list = CRUD.get_pizza_list(db,get_all)
    for pizza in pizza_list:
        pizza.ingredient_number = len(pizza.ingredients)
    return pizza_list

@app.get("/pizzas/{pizza_id}", response_model = schemas.PizzaDetails)
def show_pizza_details(pizza_id: int, db: Session = Depends(get_db)) -> schemas.PizzaDetails :#user: models.User = Depends(get_current_user)
    """
    Endpoint to retrieve details of a specific pizza by ID.
    
    Parameters:
    - pizza_id: The ID of the pizza to retrieve.
    - db: Database session dependency.

    Returns:
    - Details of the pizza.
    """
    pizza_detail = CRUD.get_pizza(db, pizza_id)
    
    if pizza_detail is None:
        raise HTTPException(status_code=404, detail = "Pizza not found")
    
    return pizza_detail

@app.post("/pizzas/",response_model = schemas.Pizza)
def create_pizza(new_pizza: schemas.PizzaCreate, db: Session = Depends(get_db)) -> schemas.Pizza:#user: models.User = Depends(get_current_user)
    """
    Endpoint to create a new pizza.

    Parameters:
    - new_pizza: The details of the new pizza to create.
    - db: Database session dependency.

    Returns:
    - The created pizza.
    """
    
    return CRUD.create_pizza(db, new_pizza)

@app.patch("/pizzas/{pizza_id}", response_model = schemas.PizzaDetails)
def change_pizza(pizza_id: int, name: str | None = None, price: int | None = None, is_active: bool | None = None, db: Session = Depends(get_db)) -> schemas.PizzaDetails:#user: models.User = Depends(get_current_user)
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
    
    pizza_detail = CRUD.get_pizza(db, pizza_id)
    if pizza_detail is None:
        raise HTTPException(status_code=404, detail="Pizza not found.")
    pizza_detail = CRUD.change_pizza(db, pizza_detail, name, price, is_active)
    return pizza_detail


#Ingredient CRUD
@app.post("/ingredients", response_model = schemas.IngredientCreate)
def create_ingredient(new_ingredient: schemas.IngredientBase, db: Session = Depends(get_db)) -> schemas.IngredientCreate:
    """
    Endpoint to create a new ingredient

    Parameters:
    - new_ingredient: The details of the new ingredient to create.
    - db: Database session dependency.

    Returns:
    - The created ingredient.
    """
    return CRUD.create_ingredient(db,new_ingredient)

@app.patch("/ingredients/{ingredient_id}",response_model = schemas.IngredientBase)
def change_ingredient(ingredient_id: int, name: str | None = None, category: str | None = None, db: Session = Depends(get_db)) -> schemas.IngredientBase:#user: models.User = Depends(get_current_user)
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
    ingredient = CRUD.get_ingredient(db,ingredient_id)
    if ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found.")
    ingredient = CRUD.change_ingredient(db, ingredient, name, category)
    return ingredient
    
@app.delete("/ingredients/{ingredient_id}")
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)) -> dict: #user: models.User = Depends(get_current_user)
    """
    Endpoint to delete an ingredient.

    Parameters:
    - ingredient_id: The ID of the ingredient to delete.
    - db: Database session dependency.

    Returns:
    - Status of the deletion.
    """
    ingredient = CRUD.get_ingredient(db, ingredient_id)
    if ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found.")
    deleted = CRUD.delete_ingredient(db,ingredient)
    if deleted:
        return {
                "status" : "completed", 
                "detail" : f"Ingredient {ingredient.name} with id {ingredient.id} deleted"
                }
    
    raise HTTPException (status_code=409, detail="Cannot delete an ingredient in an active pizza")

#Pizza-ingredient association
@app.post("/pizzas/ingredients/{pizza_id}/{ingredient_id}")
def add_ingredient_to_pizza(pizza_id : int, ingredient_id: int, db: Session = Depends(get_db)) -> dict : #user: models.User = Depends(get_current_user)
    """
    Endpoint to add an ingredient to a pizza.

    Parameters:
    - pizza_id: The ID of the pizza.
    - ingredient_id: The ID of the ingredient to add.
    - db: Database session dependency.

    Returns:
    - The created association between the pizza and ingredient.
    """
    association = CRUD.get_pizza_ing_association(db, pizza_id, ingredient_id)
    if association:
        raise HTTPException(status_code=400, detail="Association already exists")
    new_association = CRUD.add_pizza_ing_association(db, pizza_id, ingredient_id)
    return new_association

@app.delete("/pizzas/ingredients/{pizza_id}/{ingredient_id}")
def remove_ingredient_to_pizza(pizza_id : int, ingredient_id: int, db: Session = Depends(get_db)) -> dict: #user: models.User = Depends(get_current_user)
    """
    Endpoint to remove an ingredient from a pizza.

    Parameters:
    - pizza_id: The ID of the pizza.
    - ingredient_id: The ID of the ingredient to remove.
    - db: Database session dependency.

    Returns:
    - Status of the removal.
    """
    association = CRUD.get_pizza_ing_association(db, pizza_id, ingredient_id)
    if not(association):
        raise HTTPException(status_code=404, detail="Association not found")
    CRUD.delete_pizza_ing_association(db, association)
    return {
            "status" : "completed", 
            "detail" : f"Ingredient {association.ingredient_id} removed from pizza {association.pizza_id}"
            }


    