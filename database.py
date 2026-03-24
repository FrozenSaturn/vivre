import pandas as pd
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Setup Database Connection
DATABASE_URL = "sqlite:///./stock_app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Define the Product Model (The Table Structure)
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String, index=True)
    name = Column(String, index=True)
    stock = Column(Float)
    price = Column(Float)

# 3. Initialize and Seed Data
def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(Product).count() == 0:
        import random
        df = pd.read_csv('test_item.csv')
        for _, row in df.iterrows():
            item = Product(
                item_code=str(row['Item ID']),
                name=str(row['Item ID2']),
                stock=float(row['Stock On Hand']),
                price=round(random.uniform(100, 1000), 2) 
            )
            db.add(item)
        db.commit()
    db.close()

def get_product_by_code(db, search_term: str):
    # Use 'ilike' or 'contains' to be case-insensitive
    # We search for the 4-digit code within the full name (e.g., '2001' in 'Android2001 vivo')
    return db.query(Product).filter(Product.name.contains(search_term)).first()