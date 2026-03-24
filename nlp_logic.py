import re

def process_message(message: str):
    msg = message.lower().strip()
    
    # 1. Define Keyword Groups
    stock_keywords = ["stock", "available", "pcs", "units", "nos", "have", "qty", "quantity", "confirm", "ready", "hai", "check", "milega", "total", "update", "discontinued", "damage", "available", "batch", "lot", "shade", "lr"]
    action_keywords = ["block", "bhej", "dispatch", "need", "chahiye", "add", "req", "required", "urgent", "pack", "order", "karo"]
    price_keywords = ["price", "rate", "cost", "kitna", "bhau"]
    non_actionable_keywords = ["hello", "hi", "reply", "update soon", "pls", "please"]

    # 2. Extraction: Product Code, Brand, and Quantity
    # Codes are 4 consecutive digits
    codes = re.findall(r"\b\d{4}\b", msg)
    
    brands_list = ["vivo", "oppo", "samsung", "redmi", "realme", "apple", "iphone", "xiaomi", "oneplus"]
    found_brands = []
    # Using simple split to match whole words and preserve order
    for token in re.findall(r"\b[a-z]+\b", msg):
        if token in brands_list:
            found_brands.append(token)

    # 3. Extract quantity
    # Find all standalone numbers not in codes
    numbers = []
    for match in re.finditer(r"\b\d+\b", msg):
        val = match.group()
        if len(val) == 4 and val in codes:
            continue
        numbers.append(int(val))
    
    # In queries like "79 me se 30 block" or "150 me se 80", the latter number is usually the requested quantity
    quantity = None
    if numbers:
        quantity = numbers[-1]

    # Handle multiple queries by zipping codes and brands
    queries = []
    max_len = max(len(codes), len(found_brands))
    if max_len == 0:
        queries = [{"product_query": ""}] 
    else:
        for i in range(max_len):
            c = codes[i] if i < len(codes) else ""
            b = found_brands[i] if i < len(found_brands) else ""
            query_str = f"{c} {b}".strip()
            queries.append({"product_query": query_str})

    # For singular backwards compatibility
    product_query = queries[0]["product_query"] if queries else ""

    # 4. Determine Intent based on keywords
    intent = "unknown"
    
    wants_price = any(word in msg for word in price_keywords)
    wants_stock = any(word in msg for word in stock_keywords) or any(word in msg for word in action_keywords) or quantity is not None
    
    if not codes and not found_brands:
        if any(word in msg for word in non_actionable_keywords):
            intent = "non_actionable"
        # Edge case: maybe words only, but no known brand or code
        elif any(word in msg for word in price_keywords + stock_keywords + action_keywords):
            intent = "check_stock" # default to stock check if no entities but has intent words
    elif wants_price and wants_stock:
        intent = "check_stock_and_price"
    elif wants_price:
        intent = "check_price"
    elif wants_stock or codes or found_brands:
        intent = "check_stock"

    return {
        "intent": intent,
        "product_query": product_query,
        "queries": queries,  # exposed for handling multiple
        "quantity": quantity
    }