from sqlalchemy.orm import Session, joinedload

from . import models,schemas,utils


#Session let us declare a db object, and have some type checks

#User
def get_user(db: Session, user_id: int) -> models.User:
    """
    Retrieve a user by user ID.

    Parameters:
    - db: SQLalchemy Session
    - user_id: ID of the user

    Returns:
    - User model
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> models.User:
    """
    Retrieve a user by user username.

    Parameters:
    - db: SQLalchemy Session
    - username: username of the user

    Returns:
    - User model
    """
    return db.query(models.User).filter(
        models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Create a new user.

    Parameters:
    - db: SQLalchemy Session
    - user: UserCreate model

    Returns:
    - Created User model
    """
    #password = get from a token
    _password = user.password
    print(_password)
    hashed_password = utils.get_hashed_password(_password)
    user_db = models.User(username = user.username, password = hashed_password)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db

def modify_user_permission(
        db : Session, user: schemas.User, 
        level: models.UserType) -> models.User:
    
    user.permission_level = level
    db.commit()
    db.refresh(user)
    
    return user


#Pizza
def get_pizza_list(db: Session, get_all: bool) -> list[models.Pizza]:
    """
    Retrieve a list of pizzas from the database.

    Parameters:
    - db: SQLalchemy Session
    - get_all: Flag to determine whether to fetch all pizzas or only active ones

    Returns:
    - List of Pizza models
    """
    if get_all:
        pizzas_db = db.query(models.Pizza).options(
            joinedload(models.Pizza.ingredients)).all()
    else:
        pizzas_db = db.query(models.Pizza).join(
            models.Pizza.ingredients).filter(models.Pizza.is_active).options(
            joinedload(models.Pizza.ingredients)).all()
    return pizzas_db


def get_pizza(db: Session, pizza_id: int) -> models.Pizza:
    """
    Retrieve a pizza by its ID.

    Parameters:
    - db: SQLalchemy Session
    - pizza_id: ID of the pizza

    Returns:
    - Pizza model
    """
    pizza = db.query(models.Pizza).filter(models.Pizza.id == pizza_id).first()
    if pizza is None:
        return None
    ingredients_names = [
        association.ingredient.name for association in pizza.ingredients
    ]
    pizza.ingredients_names = ingredients_names
    return pizza

def get_pizza_by_name(db: Session, pizza_name: str) -> models.Pizza:
    """
    Retrieve a pizza by its ID.

    Parameters:
    - db: SQLalchemy Session
    - pizza_id: ID of the pizza

    Returns:
    - Pizza model
    """
    pizza = db.query(models.Pizza).filter(models.Pizza.name == pizza_name).first()
    if pizza is None:
        return None
    ingredients_names = [
        association.ingredient.name for association in pizza.ingredients
    ]
    pizza.ingredients_names = ingredients_names
    return pizza

def create_pizza(db: Session, pizza: schemas.PizzaCreate) -> models.Pizza:
    """
    Create a new pizza.

    Parameters:
    - db: SQLalchemy Session
    - pizza: PizzaCreate model

    Returns:
    - Created Pizza model
    """
    pizza = models.Pizza(**pizza.dict()) #fastapi recommended implementation 
    db.add(pizza)
    db.commit()
    db.refresh(pizza)
    return pizza

def change_pizza(
        db: Session, pizza_detail, name, price, is_active) -> models.Pizza:
    """
    Update the details of a pizza.

    Parameters:
    - db: SQLalchemy Session
    - pizza_detail: Pizza model
    - name: New name for the pizza (optional)
    - price: New price for the pizza (optional)
    - is_active: New active status for the pizza (optional)

    Returns:
    - Updated Pizza model
    """
    
    if name is not None :
        pizza_detail.name = name
    if price is not None:
        pizza_detail.price = price
    if is_active is not None:
        pizza_detail.is_active = is_active
    
    
    db.commit()
    db.refresh(pizza_detail)
    
    return pizza_detail

#Ingredients
def create_ingredient(
        db: Session, 
        new_ingredient = schemas.IngredientBase) -> models.Ingredient:
    """
    Create a new ingredient.

    Parameters:
    - db: SQLalchemy Session
    - new_ingredient: IngredientBase model

    Returns:
    - Created Ingredient model
    """
    new_ingredient = models.Ingredient(**new_ingredient.dict()) 
    #fastapi recommended implementation 
    db.add(new_ingredient)
    db.commit()
    db.refresh(new_ingredient)
    return new_ingredient

def get_ingredient(db: Session, ingredient_id: int) -> models.Ingredient:
    """
    Retrieve an ingredient by its ID.

    Parameters:
    - db: SQLalchemy Session
    - ingredient_id: ID of the ingredient

    Returns:
    - Ingredient model
    """
    ingredient = db.query(models.Ingredient).filter(
        models.Ingredient.id == ingredient_id).first()
    if ingredient is None:
        return None
    return ingredient

def get_ingredient_by_name(db: Session, ingredient_name: int) -> models.Ingredient:
    """
    Retrieve an ingredient by its ID.

    Parameters:
    - db: SQLalchemy Session
    - ingredient_id: ID of the ingredient

    Returns:
    - Ingredient model
    """
    ingredient = db.query(models.Ingredient).filter(
        models.Ingredient.name == ingredient_name).first()
    if ingredient is None:
        return None
    return ingredient

def change_ingredient(
        db: Session, ingredient, name=None, category=None) -> models.Ingredient:
    """
    Update the details of an ingredient.

    Parameters:
    - db: SQLalchemy Session
    - ingredient: Ingredient model
    - name: New name for the ingredient (optional)
    - category: New category for the ingredient (optional)

    Returns:
    - Updated Ingredient model
    """
    
    if name is not(None):
        ingredient.name = name
    if category is not(None):
        ingredient.category = category
    
    
    db.commit()
    db.refresh(ingredient)
    
    return ingredient

def delete_ingredient(db: Session, ingredient: models.Ingredient) -> bool:
    """
    Delete an ingredient.

    Parameters:
    - db: SQLalchemy Session
    - ingredient: Ingredient model

    Returns:
    - True if the ingredient is deleted successfully, False otherwise
    """
    active_pizzas = [
        association.pizza for association in ingredient.pizzas 
        if association.pizza.is_active 
    ]
    
    if len(active_pizzas) == 0:
        ingredients_db = db.query(models.Ingredient).filter(
            models.Ingredient.id==ingredient.id).first()
        db.delete(ingredients_db)
        db.commit()
        return True
    return False


#Associations
def get_pizza_ing_association(
        db: Session, pizza_id: int, 
        ingredient_id: int) -> models.PizzaIngredientAssociation:
    """
    Retrieve the association between a pizza and an ingredient.

    Parameters:
    - db: SQLalchemy Session
    - pizza_id: ID of the pizza
    - ingredient_id: ID of the ingredient

    Returns:
    - PizzaIngredientAssociation model
    """
    association = db.query(models.PizzaIngredientAssociation).filter(
        models.PizzaIngredientAssociation.pizza_id==pizza_id, 
        models.PizzaIngredientAssociation.ingredient_id==ingredient_id).first()
    return association

def add_pizza_ing_association(
        db: Session, pizza_id: int, 
        ingredient_id: int) -> models.PizzaIngredientAssociation:
    """
    Create a new association between a pizza and an ingredient.

    Parameters:
    - db: SQLalchemy Session
    - pizza_id: ID of the pizza
    - ingredient_id: ID of the ingredient

    Returns:
    - Created PizzaIngredientAssociation model
    """
    dict = {
        'pizza_id' : pizza_id,
        'ingredient_id' : ingredient_id
    }

    pizza_ing_db = models.PizzaIngredientAssociation(**dict)
    print(pizza_ing_db)
    db.add(pizza_ing_db)
    db.commit()
    db.refresh(pizza_ing_db)

    return pizza_ing_db

def delete_pizza_ing_association(
        db: Session, association: models.PizzaIngredientAssociation):
    """
    Delete an association between a pizza and an ingredient.

    Parameters:
    - db: SQLalchemy Session
    - association: PizzaIngredientAssociation model
    """

    db.delete(association)
    db.commit()


#def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#    db_item = models.Item(**item.dict(), owner_id=user_id)
#    db.add(db_item)
#    db.commit()
#    db.refresh(db_item)
#    return db_item



