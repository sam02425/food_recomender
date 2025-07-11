from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import relationship
from backend.app.db import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    items = Column(JSON, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String, default="Pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="orders")

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, total={self.total})>"
