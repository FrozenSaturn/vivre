import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load the Gemini API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def process_message(message: str):
    system_prompt = """You are a Stock Assistant Parser for a warehouse management system. 
Your task is to parse user messages and extract structured information to query a SQL database.

### 1. Intent Classification
Classify the user's intent into exactly ONE of the following:
- "check_stock": User asks about availability, current stock, or quantity on hand.
- "check_price": User asks about the rate, cost, price, or "bhau".
- "check_stock_and_price": User asks for both (e.g., "What is the price and is it in stock?").
- "non_actionable": Greetings (Hi/Hello), filler text, or unrelated requests (e.g., "update soon").

### 2. Entity Extraction
- "product_query": Extract the core item name or alphanumeric code. 
  * CRITICAL: Strip filler words like "item", "product", "code", "units", "pcs", "nos". 
  * Example: "item 2006" -> "2006". "vivo 2001" -> "vivo 2001".
- "quantity": Extract ONLY the numeric value for the requested stock. If no number is mentioned, return null.

### 3. Logic & Multilingual Rules
- Support Multiple Items: If the user mentions multiple products (e.g., "2001 and 2002 stock?"), extract all into the "queries" list.
- Hinglish Support: Correcty map Hindi/English hybrid terms to intents:
  * "hai kya", "milega", "stock batao" -> check_stock
  * "rate kya hai", "kitna ka hai" -> check_price
- Handling Variations: Recognize generic examples from the brief like "Item ABC" or "Item X" as valid product_query entities.

### 4. Output Format (Strict JSON)
You MUST return the entire response as a valid JSON object. Do not include markdown formatting, code blocks, or explanatory text. The response must start with '{' and end with '}'.

JSON Structure:
{
  "intent": "check_stock_and_price",
  "product_query": "Primary Item Name",
  "quantity": 50,
  "queries": [
    {"product_query": "Item 1", "quantity": 50},
    {"product_query": "Item 2", "quantity": 50}
  ]
}
"""

    try:
        # We prepend the system prompt to the user message to ensure compatibility
        full_prompt = f"{system_prompt}\n\nUser Message: {message}"
        
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Generation config to encourage JSON output
        response = model.generate_content(
            full_prompt,
            generation_config={"response_mime_type": "application/json", "temperature": 0.0}
        )
        
        # Parse the JSON response
        result = json.loads(response.text)
        
        intent = result.get("intent", "unknown")
        product_query = result.get("product_query", "")
        quantity = result.get("quantity", None)
        queries = result.get("queries", [])
        
        # Ensure 'queries' is a list of dicts with 'product_query'
        if not queries and product_query:
            queries = [{"product_query": product_query}]
            
        return {
            "intent": intent,
            "product_query": product_query,
            "queries": queries,
            "quantity": quantity
        }
        
    except Exception as e:
        # Basic error handling: catch API failure or malformed JSON
        print(f"Error in Gemini parsing: {e}")
        return {
            "intent": "unknown",
            "product_query": "",
            "queries": [],
            "quantity": None
        }