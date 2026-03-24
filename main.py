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

        if nlp_result["intent"] in ["check_stock", "check_price", "check_stock_and_price"]:
            queries = nlp_result.get("queries", [])
            results = []
            
            for q in queries:
                q_str = q.get("product_query", "")
                if not q_str:
                    continue
                product = get_product_by_code(db, q_str)
                
                if not product:
                    results.append({
                        "item_name": q_str,
                        "status": "Product Not Found"
                    })
                    continue
                
                qty = nlp_result.get("quantity")
                stock_res = {
                    "item_name": product.name,
                    "available": product.stock,
                    "status": "Available" if (qty is None or product.stock >= qty) else "Insufficient"
                }

                if "price" in nlp_result["intent"]:
                    stock_res["price"] = product.price
                
                results.append(stock_res)

            if not results:
                 return {"interpreted_intent": nlp_result["intent"], "stock_result": "Product Not Found"}

            return {
                "interpreted_intent": nlp_result["intent"],
                "extracted_entities": {
                    "queries": [q.get("product_query", "") for q in queries],
                    "requested_qty": nlp_result.get("quantity")
                },
                "stock_result": results
            }
        
        return {"interpreted_intent": nlp_result["intent"], "stock_result": "Could not understand your request."}
    except Exception as e:
        logging.error(f"Error processing chat: {e}")
        return {"error": "Internal server error", "details": str(e)}