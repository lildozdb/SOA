from sqlalchemy import Column, String, Numeric, Integer, Enum, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from src.database import Base
import enum

class ProductStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"

class DBProduct(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(255), nullable=False)
    description = Column(String(4000), nullable=True)
    price = Column(Numeric(12, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    category = Column(String(100), nullable=False)
    status = Column(Enum(ProductStatus, name="product_status"), nullable=False, default=ProductStatus.ACTIVE)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)