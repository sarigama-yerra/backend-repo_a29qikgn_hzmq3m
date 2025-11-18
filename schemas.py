"""
Database Schemas for Handmade Kids Products Store

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name (e.g., Product -> "product").

These schemas are used for validation before inserting into the database.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product"
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Detailed product description")
    price: float = Field(..., ge=0, description="Price in USD")
    category: str = Field(..., description="Category like 'toys', 'plush', 'educational'")
    images: List[str] = Field(default_factory=list, description="Array of image URLs")
    in_stock: bool = Field(True, description="Whether product is available")
    stock: int = Field(0, ge=0, description="Units in stock")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating 0-5")
    age_range: Optional[str] = Field(None, description="Recommended age range, e.g., '3-6 years'")
    materials: List[str] = Field(default_factory=list, description="Primary materials used")
    featured: bool = Field(False, description="Whether product is featured on the home page")

class Customer(BaseModel):
    """
    Customers collection schema
    Collection name: "customer"
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Shipping address")
    phone: Optional[str] = Field(None, description="Phone number")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    title: str = Field(..., description="Snapshot of product title at purchase time")
    image: Optional[str] = Field(None, description="Primary image URL")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    price: float = Field(..., ge=0, description="Unit price at purchase time")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    customer: Customer
    items: List[OrderItem]
    subtotal: float = Field(..., ge=0)
    shipping: float = Field(0, ge=0)
    total: float = Field(..., ge=0)
    status: str = Field("pending", description="Order status: pending, paid, shipped, delivered, cancelled")
