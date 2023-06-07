from sqlalchemy.orm import Session, joinedload

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
        pizzas_db = db.query(models.Pizza).options(joinedload(models.Pizza.ingredients)).all()
    else:
        pizzas_db = db.query(models.Pizza).join(
            models.Pizza.ingredients).filter(
            models.Pizza.is_active).options(
            joinedload(models.Pizza.ingredients)).all()
    return pizzas_db

def get_pizza(db: Session, pizza_id: int):
    """
    To complete
    """
    pizza = db.query(models.Pizza).filter(models.Pizza.id == pizza_id).first()
    if pizza is None:
        return None
    ingredients_names = [association.ingredient.name for association in pizza.ingredients]
    pizza.ingredients_names = ingredients_names



    return pizza

def create_pizza(db: Session, pizza: schemas.PizzaCreate):
    pizza = models.Pizza(**pizza.dict()) #fastapi recommended implementation 
    db.add(pizza)
    db.commit()
    db.refresh(pizza)
    return pizza

def change_pizza(db: Session, pizza_detail, name, price, is_active):
    print(price)
    
    if name is not(None):
        pizza_detail.name = name
    if price is not(None):
        pizza_detail.price = price
    if is_active is not(None):
        pizza_detail.is_active = is_active
    
    
    db.commit()
    db.refresh(pizza_detail)
    
    return pizza_detail

#def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#    db_item = models.Item(**item.dict(), owner_id=user_id)
#    db.add(db_item)
#    db.commit()
#    db.refresh(db_item)
#    return db_item



