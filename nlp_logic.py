import re

def process_message(message: str):
    msg = message.lower().strip()
    
    # 1. Handle "Non-actionable" messages (Source: Brief )
    # Ignore messages that don't ask for stock or price
    non_actionable_keywords = ["update soon", "confirm", "hello", "hi"]
    if any(word in msg for word in non_actionable_keywords):
        return {"intent": "non_actionable", "product": None, "quantity": None}

    # 2. Improved Regex for variations like "2004 20 nos chahiye"
    # This looks for: [4 digits] followed by [some space] followed by [digits]
    # It ignores words like "pcs", "box", or "nos" that come after.
    pattern = r"(\d{4})\s+(\d+)"
    match = re.search(pattern, msg)
    
    if match:
        return {
            "intent": "check_stock",
            "product": match.group(1),
            "quantity": int(match.group(2))
        }
    
    return {"intent": "unknown", "product": None, "quantity": None}