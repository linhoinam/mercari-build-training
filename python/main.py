import os
import json
import hashlib
import logging
import pathlib
import sqlite3
from fastapi import FastAPI, Form, HTTPException, UploadFile, File, Path, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

## Step 5.1 Write into a database
DB_FILE = "/Users/catherine/Desktop/mercari-build-training/db/mercari.sqlite3"

# Connection with db
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Set JSON file name & image location
DATA_FILE = "items.json"
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True) 

app = FastAPI()

origins = [os.environ.get("FRONT_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Read JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    else:
        return {"items": []} 

# Save JSON
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Define Item name,category,image_name
class Item(BaseModel):
    name: str
    category: str
    image_name: str = None 

## Step 5.1 Write into a database
def insert_item(item: Item, image_name: str = None):
    conn = get_db()
    cursor = conn.cursor()

    ## Step 5.8 Move the category information to a separate table
    # Find out the catergory
    cursor.execute("SELECT id FROM categories WHERE name = ?", (item.category,))
    category = cursor.fetchone()

    # If there is no category, insert an item category
    if category is None:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (item.category,))
        category_id = cursor.lastrowid
    else:
        category_id = category["id"]

    # Insert item（using category_id）
    cursor.execute(
        "INSERT INTO items (name, category_id, image_name) VALUES (?, ?, ?)",
        (item.name, category_id, image_name),
    )

    conn.commit()
    conn.close()

## Step 4.4 Add Item Images
@app.post("/items")
def add_item(
    name: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(None),
):
    ## Step 5.1  Write into a database
    image_name = None
    if image:
        image_bytes = image.file.read()
        image_hash = hashlib.sha256(image_bytes).hexdigest()
        image_name = f"{image_hash}.jpg"
        with open(f"{IMAGE_DIR}/{image_name}", "wb") as f:
            f.write(image_bytes)

    insert_item(Item(name=name, category=category), image_name) 
    return {"message": f"Item received: {name}"}

## Step 5.1  Write into a database
@app.get("/items")
def get_items():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    conn.close()
    return {"items": [dict(item) for item in items]}

## Step 4.5 Return Item Details
@app.get("/items/{item_id}")
def get_item(item_id: int = Path(..., description="The ID of the item to retrieve")):
    data = load_data()
    if 0 <= item_id < len(data["items"]):
        return data["items"][item_id2]
    else:
        raise HTTPException(status_code=404, detail="Item not found")

# Step 4.6 (Optional) Understand Loggers -- Configure logging to show debug messages
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.get("/image/{image_name}")
async def get_image(image_name: str):
    image_path = f"{IMAGE_DIR}/{image_name}"

    if not os.path.exists(image_path):
        # Log the error message when the image is not found
        logger.debug(f"Image not found: {image_path}")
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(image_path)

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

## Step 5.2 Search for an item
@app.get("/search")
def search_items(keyword: str = Query(..., description="Keyword to search for items")):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
    """
    SELECT items.id, items.name, categories.name AS category, items.image_name 
    FROM items 
    JOIN categories ON items.category_id = categories.id
    WHERE items.name LIKE ? OR categories.name LIKE ?
    """, 
    (f"%{keyword}%", f"%{keyword}%")
    )
    items = cursor.fetchall()
    conn.close()
    
    return {"items": [dict(item) for item in items]}