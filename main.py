import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order

app = FastAPI(title="Handmade Kids Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Handmade Kids Store Backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# ---------- Product Endpoints ----------

@app.post("/api/products", response_model=dict)
def create_product(product: Product):
    try:
        inserted_id = create_document("product", product)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ProductQuery(BaseModel):
    category: Optional[str] = None
    featured: Optional[bool] = None
    search: Optional[str] = None
    limit: Optional[int] = 20

@app.post("/api/products/search")
def search_products(query: ProductQuery):
    try:
        filter_dict = {}
        if query.category:
            filter_dict["category"] = query.category
        if query.featured is not None:
            filter_dict["featured"] = query.featured
        if query.search:
            # Basic text search across title and description
            filter_dict["$or"] = [
                {"title": {"$regex": query.search, "$options": "i"}},
                {"description": {"$regex": query.search, "$options": "i"}},
            ]
        limit = query.limit or 20
        products = get_documents("product", filter_dict, limit)
        for p in products:
            p["_id"] = str(p["_id"])  # serialize ObjectId
        return {"items": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}")
def get_product(product_id: str):
    try:
        from bson import ObjectId
        if not ObjectId.is_valid(product_id):
            raise HTTPException(status_code=400, detail="Invalid product id")
        items = get_documents("product", {"_id": ObjectId(product_id)}, limit=1)
        if not items:
            raise HTTPException(status_code=404, detail="Product not found")
        item = items[0]
        item["_id"] = str(item["_id"])
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Orders Endpoints ----------

@app.post("/api/orders", response_model=dict)
def create_order(order: Order):
    try:
        inserted_id = create_document("order", order)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
