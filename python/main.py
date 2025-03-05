import os
import json
import hashlib
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException, UploadFile, File, Path
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

## 2. List a new item
def insert_item(item: Item, image: UploadFile = None):
    data = load_data()
    image_name = None

    # Hash the image using SHA-256, and save it with the name `<hashed-value>.jpg`
    if image:
        image_bytes = image.file.read()
        image_hash = hashlib.sha256(image_bytes).hexdigest()
        image_name = f"{image_hash}.jpg"
        with open(f"{IMAGE_DIR}/{image_name}", "wb") as f:
            f.write(image_bytes)

    # Create new item, add image_name
    new_item = {"name": item.name, "category": item.category, "image_name": image_name}
    data["items"].append(new_item) 
    save_data(data) 

## 4. Add Item Images
@app.post("/items")
def add_item(
    name: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(None),
):
    insert_item(Item(name=name, category=category), image) 
    return {"message": f"Item received: {name}"}

## 3. Get the List of Items
@app.get("/items")
def get_items():
    return load_data() 

## 5. Return Item Details
@app.get("/items/{item_id}")
def get_item(item_id: int = Path(..., description="The ID of the item to retrieve")):
    data = load_data()
    if 0 <= item_id < len(data["items"]):
        return data["items"][item_id]
    else:
        raise HTTPException(status_code=404, detail="Item not found")

# 6. (Optional) Understand Loggers -- Configure logging to show debug messages
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
