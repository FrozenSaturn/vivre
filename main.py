from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, init_db, Product
from nlp_logic import process_message
from database import get_product_by_code
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Chat Stock Bot")

# Initialize DB on startup
@app.on_event("startup")
def startup():
    init_db()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request Model
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        nlp_result = process_message(request.message)
        
        if nlp_result["intent"] == "non_actionable":
            return {"interpreted_intent": "non_actionable", "stock_result": None}

        if nlp_result["intent"] == "check_stock":
            product = get_product_by_code(db, nlp_result["product"])
            
            if not product:
                return {"intent": "check_stock", "stock_result": "Not Found"}
            
            # Final JSON structure per project requirements 
            return {
                "interpreted_intent": "check_stock",
                "extracted_entities": {
                    "product_id": nlp_result["product"],
                    "requested_qty": nlp_result["quantity"]
                },
                "stock_result": {
                    "item_name": product.name,
                    "available": product.stock,
                    "status": "Available" if product.stock >= nlp_result["quantity"] else "Insufficient"
                }
            }
    except Exception as e:
        logging.error(f"Error processing chat: {e}")
        return {"error": "Internal server error", "details": str(e)}