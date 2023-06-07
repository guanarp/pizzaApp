from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from . import CRUD, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)

#create a dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/") #home endpoint
def home():
    return {"Welcome": "to the pizza app"}

@app.get("/pizzas", response_model=List[schemas.Pizza])
def show_pizzas(db: Session = Depends(get_db)
                ): #user: models.User = Depends(get_current_user)
    """
    Checks if the request from a regular user or staff/SU \n
    If staff/SU shows ALL pizzas \n
    else only active pizzas
    """
    get_all = True
    #if user.permission_level != 1:
    #    get_all = True
    pizza_list = CRUD.get_pizza_list(db,get_all)
    for pizza in pizza_list:
        pizza.ingredient_number = len(pizza.ingredients)
    return pizza_list

@app.get("/pizzas/{pizza_id}", response_model = schemas.PizzaDetails)
def show_pizza_details(pizza_id: int, db: Session = Depends(get_db)):#user: models.User = Depends(get_current_user)
    """
    To complete
    """
    pizza_detail = CRUD.get_pizza(db, pizza_id)
    
    if pizza_detail is None:
        raise HTTPException(status_code=404, detail = "Pizza not found")
    
    return pizza_detail
