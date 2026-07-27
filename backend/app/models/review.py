from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    review = Column(String, nullable=False)
    sentiment = Column(String, nullable=False, default="neutral")

    def __repr__(self):
        return f"<Review(id={self.id}, product_id={self.product_id}, sentiment='{self.sentiment}')>"