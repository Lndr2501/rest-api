from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from enum import Enum
from jose import jwt
from typing import Optional

items = [
    {"name": "Coffee", "price": 2, "typ": "drink"},
    {"name": "Coca Cola", "price": 3, "typ": "drink"},
    {"name": "Minecraft", "price": 25, "typ": "game"}
]


class Type(Enum):
    drink = "drink"
    game = "game"


class Item(BaseModel):
    name: str = Field("Name", min_length=1, max_length=50)
    price: int = Field(1, gt=0, lt=100)
    typ: Type


class ResponeItem(BaseModel):
    name: str
    typ: Type


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends()):
    if data.username == "admin" and data.password == "admin":
        access_token = jwt.encode({"username": data.username}, "secret")
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.get("/items")
async def itemstwo(category: Optional[str] = None):
    if category:
        data = []
        for item in items:
            if item["typ"].lower().startswith(category.lower()):
                data.append(item)
        return data
    return items


@app.get("/items/{item_id}")
async def item(item_id: int):
    return items[item_id]


@app.post("/items/", response_model=ResponeItem)
async def create_item(data: Item, token: str = Depends(oauth2_scheme)):
    user = jwt.decode(token, "secret")
    if user["username"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    items.append(data)
    return data


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    items[item_id] = item
    return item


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    items.pop(item_id)
    return {"message": "Item deleted"}

app.run()
