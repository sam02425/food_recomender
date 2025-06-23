from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Any
from app.db import SessionLocal
from app.models.order import Order
from app.api.auth import get_current_user, get_db
from app.models.user import User

router = APIRouter(prefix="/api/orders", tags=["orders"])

# Pydantic Schemas
class OrderItem(BaseModel):
    name: str
    quantity: int = 1
    price: float

class OrderCreate(BaseModel):
    items: List[Any]  # Accepts list of dicts for now
    total: float

class OrderOut(BaseModel):
    id: int
    items: List[Any]
    total: float
    status: str
    created_at: str
    class Config:
        orm_mode = True

@router.post("/start-order")
async def start_order():
    """
    Initialize a new order session.
    This endpoint is used to start a new order process.
    """
    return {"status": "success", "message": "Order session started"}

@router.post("/", response_model=OrderOut)
def place_order(order: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_order = Order(
        user_id=current_user.id,
        items=order.items,
        total=order.total,
        status="Pending"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[OrderOut])
def get_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
