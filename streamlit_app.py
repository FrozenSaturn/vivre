import streamlit as st
import requests

st.title("📦 Stock Assistant Chatbot")

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about stock or price..."):
    # Display user message in chat message container
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call FastAPI backend
    try:
        response = requests.post("http://127.0.0.1:8000/chat", json={"message": prompt})
        data = response.json()
        
        # Simple parsing of the returned result as requested
        if "error" in data:
            bot_response = f"Error: {data['details']}"
        elif data.get("stock_result") is None:
             bot_response = "I couldn't find any actionable intent in your message."
        elif isinstance(data["stock_result"], str):
             bot_response = data["stock_result"]
        elif isinstance(data["stock_result"], list):
            bot_response = ""
            for res in data["stock_result"]:
                bot_response += f"**Item:** {res.get('item_name')}\n\n"
                if res.get("status") == "Product Not Found":
                    bot_response += "⚠️ Product Not Found\n\n---\n\n"
                    continue
                bot_response += f"**Available:** {res.get('available')}\n"
                bot_response += f"**Status:** {res.get('status')}\n"
                if "price" in res:
                    bot_response += f"**Price:** ${res.get('price')}\n"
                bot_response += "\n---\n\n"
        else:
            bot_response = str(data["stock_result"])
    except Exception as e:
        bot_response = f"Connection Error: Could not reach backend server at http://127.0.0.1:8000. Make sure uvicorn is running."

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(bot_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
