from . import CRUD, models, schemas

app = FastAPI()

@app.get("/") #home endpoint
def home():
    return {"Welcome": "to the pizza app"}

@app.get("/pizzas")
def show_pizzas(user: models.User):
    """
    Checks if the request from a regular user or staff/SU
    If staff/SU shows ALL pizzas
    else only active pizzas
    """
    get_all = False
    if user.is_staff or user.is_SU:
        get_all = True
    pizza_list = CRUD.get_pizzas(db,get_all)

