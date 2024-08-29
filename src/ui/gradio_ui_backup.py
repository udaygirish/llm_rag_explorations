import gradio as gr
import requests

# Define the URL of the FastAPI server
FASTAPI_URL = "http://localhost:8003"

def chat_with_bot(message, chat_type, username, password):
    # Request a token from the API
    response = requests.post(f"{FASTAPI_URL}/api/token", data={"username": username, "password": password})
    if response.status_code == 200:
        access_token = response.json()["access_token"]
    else:
        return "Login failed. Please check your username and password."

    # Send the message to the chatbot API
    payload = {
        "message": message,
        "chat_type": chat_type,
        "chatbot_hist": []  # Optionally, you can manage chat history here
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.post(f"{FASTAPI_URL}/chatbot", json=payload, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            chatbot_response = response_data.get("chatbot_hist", [])
            return chatbot_response[-1][1] if chatbot_response else "No response from chatbot."
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: Failed to communicate with the API - {str(e)}"

# Define the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# ChatAnything")
    with gr.Row():
        username = gr.Textbox(label="Username", placeholder="Enter your username")
        password = gr.Textbox(label="Password", type="password", placeholder="Enter your password")
    chat_type = gr.Dropdown(choices=[
        "Q&A with stored SQL-DB",
        "Generic",
        "Q&A with Uploaded CSV/XLSX SQL-DB",
        "Q&A with stored CSV/XLSX SQL-DB",
        "RAG with stored CSV/XLSX ChromaDB"
    ], label="Select Chat Type")
    message = gr.Textbox(label="Message", placeholder="Type your message here")
    submit_button = gr.Button("Send")
    response = gr.Textbox(label="Response", lines=10, placeholder="Chatbot response will appear here")

    # Define the action when the button is clicked
    submit_button.click(
        chat_with_bot, 
        inputs=[message, chat_type, username, password], 
        outputs=response
    )

# Launch the Gradio app
demo.launch()
