import json
from fastapi.testclient import TestClient

from .main import app

AUTHORIZATION = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODYyODI2NjUsInN1YiI6Imd1YW5hIn0.tPFrDvvf2DaI14soEmSE1bMxYUHsZQLngVyjp6d0L3A"

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Welcome": "to the pizza app"}

def test_signup():
    data = {
        "username": "testuser",
        "password": "test123",
    }
    response = client.post("/signup", json=data)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert "id" in response.json()
    assert "password" not in response.json()

def test_signup_existing_username():
    data = {
        "username": "testuser",
        "password": "testpassword",
    }
    response = client.post("/signup", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "The username already exists"

def test_login():
    data = {
        "username": "testuser",
        "password": "test123"
    }
    response = client.post("/login", data=data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

def test_login_invalid_username():
    data = {
        "username": "invaliduser",
        "password": "testpassword"
    }
    response = client.post("/login", data=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_invalid_password():
    data = {
        "username": "testuser",
        "password": "invalidpassword"
    }
    response = client.post("/login", data=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_basic():
    response = client.post("/login/basic", auth=("admin", "tdp"))
    assert response.status_code == 200
    assert response.json()["token_type"] == "basic"
    assert "access_token" in response.json()

def test_login_basic_invalid_credentials():
    response = client.post("/login/basic", auth=("admin", "invalidpassword"))
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_modify_user_permission():
    user_id = 1
    level = "staff"
    response = client.patch(
        f"/users/{user_id}?level={level}", headers={"Authorization": AUTHORIZATION})
    assert response.status_code == 200
    assert response.json()["permission_level"] == level


def test_modify_user_permission_unauthorized():
    user_id = 1
    level = "staff"
    response = client.patch(f"/users/{user_id}?level={level}")
    assert response.status_code == 401
    assert "detail" in response.json()


def test_show_pizzas():
    response = client.get("/pizzas", headers={"Authorization": AUTHORIZATION})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_show_pizza_details():
    pizza_id = 1
    response = client.get(f"/pizzas/{pizza_id}", 
                          headers={"Authorization": AUTHORIZATION})
    assert response.status_code == 200
    assert "id" in response.json()


def test_show_pizza_details_unauthorized():
    pizza_id = 1
    response = client.get(f"/pizzas/{pizza_id}")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_create_pizza():
    pizza_data = {
        "name": "Test Pizza",
        "price": 10,
        "is_active": True,
    }
    response = client.post(
        "/pizzas", json=pizza_data, headers={"Authorization": AUTHORIZATION})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Pizza"
    assert response.json()["price"] == 10

def test_create_pizza_unauthorized():
    pizza_data = {
        "name": "Test Pizza",
        "price": 10,
        "is_active": True,
    }
    response = client.post(
        "/pizzas", json=pizza_data)
    assert response.status_code == 401
    assert "detail" in response.json()



def test_update_pizza():
    pizza_id = 1
    pizza_data = {
        "name": "Updated Pizza",
        "price": 9,
        "is_active": True,
    }
    response = client.patch(
        f"/pizzas/{pizza_id}", json=pizza_data, 
        headers={"Authorization": AUTHORIZATION})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Pizza"
    assert response.json()["price"] == 9


def test_update_pizza_unauthorized():
    pizza_id = 1
    pizza_data = {
        "name": "Updated Pizza",
        "price": 9,
        "is_active": True,
    }
    response = client.patch(
        f"/pizzas/{pizza_id}", json=pizza_data)
    assert response.status_code == 401
    assert "detail" in response.json()


def test_delete_pizza():
    pizza_id = 10
    response = client.delete(
        f"/pizzas/{pizza_id}", headers={"Authorization": AUTHORIZATION})
    assert response.status_code == 200
    assert response.json()["message"] == "Pizza deleted"


def test_delete_pizza_unauthorized():
    pizza_id = 10
    response = client.delete(f"/pizzas/{pizza_id}")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_create_ingredient():
    payload = {
        "name": "New Tomato name",
        "category": "basic"
    }
    response = client.post(
        "/ingredients", json=payload, headers={"Authorization": AUTHORIZATION})
    assert response.status_code == 200
    assert response.json()["name"] == "New Tomato Name"
    assert response.json()["category"] == "basic"

def test_create_ingredient_unauthorized():
    payload = {
        "name": "New Tomato Name",
        "category": "basic"
    }
    response = client.post(
        "/ingredients", json=payload)
    assert response.status_code == 401
    assert "detail" in response.json()

def test_change_ingredient():
    ingredient_id = 1   
    payload = {
        "name": "New Tomato Name",
        "category": "premium"
    }
    response = client.patch(
        f"/ingredients/{ingredient_id}", json=payload, 
        headers={"Authorization": AUTHORIZATION})
    assert response.status_code == 200
    assert response.json()["name"] == "New Tomato Name"
    assert response.json()["category"] == "premium"

def test_change_ingredient_unauthorized():
    ingredient_id = 1   
    payload = {
        "name": "New Tomato Name",
        "category": "basic"
    }
    response = client.patch(
        f"/ingredients/{ingredient_id}", json=payload)
    assert response.status_code == 401
    assert "detail" in response.json()

def test_delete_ingredient():
    ingredient_id = 1   
    response = client.delete(
        f"/ingredients/{ingredient_id}", 
        headers={"Authorization": AUTHORIZATION})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

def test_delete_ingredient_unauthorized():
    ingredient_id = 1   
    response = client.delete(
        f"/ingredients/{ingredient_id}")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_add_ingredient_to_pizza():
    pizza_id = 1   
    ingredient_id = 1   
    response = client.post(
        f"/pizzas/ingredients/{pizza_id}/{ingredient_id}", 
        headers={"Authorization": AUTHORIZATION})
    assert response.status_code == 200
    assert "pizza_id" in response.json()
    assert "ingredient_id" in response.json()

def test_add_ingredient_to_pizza():
    pizza_id = 1   
    ingredient_id = 1   
    response = client.post(
        f"/pizzas/ingredients/{pizza_id}/{ingredient_id}")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_remove_ingredient_from_pizza():
    pizza_id = 1   
    ingredient_id = 1   
    response = client.delete(
        f"/pizzas/ingredients/{pizza_id}/{ingredient_id}", 
        headers={"Authorization": AUTHORIZATION})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

def test_remove_ingredient_from_pizza():
    pizza_id = 1   
    ingredient_id = 1   
    response = client.delete(
        f"/pizzas/ingredients/{pizza_id}/{ingredient_id}")
    assert response.status_code == 401
    assert "detail" in response.json()