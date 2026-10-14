from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Demo API")

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    price: float = Field(..., gt=0)
    in_stock: bool = True

db = {}

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Service is running"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Item not found"
        )
    return db[item_id]

@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    item_id = len(db) + 1
    data = item.model_dump()
    data["id"] = item_id
    db[item_id] = data
    return data

@app.get("/search")
def search_items(q: str | None = None, limit: int = 10):
    return {"query": q, "limit": limit}

@app.get("/secure-endpoint")
def secure_endpoint(x_api_key: str | None = None):
    if x_api_key != "secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or missing API key"
        )
    return {"access": "granted"}