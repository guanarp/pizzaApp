from sqlalchemy.orm import Session

from . import models,schemas


#Session let us declare a db object, and have some type checks

#User
def get_user(db: Session, user_id: int):
    return db.Query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Create an user

    Parameters
    ---------- 
    db: SQLalchemy Session
    user: pydantic UserCreate model

    
    Returns
    -------
    returns: SQLalchemy User model
    """
    #password = get from a token
    _password = user.password
    db_user = models.User(username = user.username, password = _password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


#Pizza
def get_pizza_list(db: Session, get_all: bool):
    """
    returns the pizzas in the db, it returns all the pizzas
    or only the active ones depending on the get_all parameter
    
    db: SQLalchemy db session
    get_all: bool 

    returns: Query object from the db Session
    """
    if get_all:
        pizzas = db.query(models.Pizza).all()
    else:
        pizzas = db.query(models.Pizza).filter(models.Pizza.is_active == True).all()
    return pizzas

def get_pizza(db: Session, pizza_id: int):
    """
    To complete
    """
    pizza = db.query(models.Pizza).filter(models.Pizza.id == pizza_id).first()
    if pizza is None:
        return None
    ingredients = []
    for ingredient in pizza.ingredient_list:
        ingredients.append(ingredient)
    pizza.ingredients = ingredients

    return pizza




