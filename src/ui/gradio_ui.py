import gradio as gr
import requests

# Define the URL of the FastAPI server
FASTAPI_URL = "http://localhost:8003"

def get_access_token(username, password):
    response = requests.post(f"{FASTAPI_URL}/api/token", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def send_message(message, chat_type, access_token):
    if not access_token:
        return "Login failed or no access token. Please check your credentials.", []

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
            chatbot_hist = response_data.get("chatbot_hist", [])
            if chatbot_hist:
                return "", [list(message) for message in chatbot_hist[-1:]]  # Ensure this is a list of tuples
            return "No response from chatbot.", []
        else:
            return f"Error: {response.status_code} - {response.text}", []
    except Exception as e:
        return f"Error: Failed to communicate with the API - {str(e)}", []

def upload_file(file, access_token):
    # Implement file handling logic here
    return "File uploaded successfully."

def process_file(file, access_token):
    # Implement file processing logic here
    return "File processed."

def handle_login(username, password):
    token = get_access_token(username, password)
    if token:
        return "Login successful!", token
    return "Login failed. Please check your credentials.", None

with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem("Chat Interface"):
            ##############
            # First ROW:
            ##############
            # Remove hardcoding for the Images and make them dynamic
            with gr.Row() as row_one:
                chatbot = gr.Chatbot(
                    [],
                    elem_id="chatbot",
                    bubble_full_width=False,
                    height=500,
                    avatar_images=(
                        "src/app_data/images/uday.png", "src/app_data/logo/j_j_logo.png")
                )
                # **Adding like/dislike icons
                chatbot.like(None, None, None)
            ##############
            # SECOND ROW:
            ##############
            with gr.Row():
                input_txt = gr.Textbox(
                    lines=4,
                    scale=8,
                    placeholder="Enter text and press enter, or upload files",
                    container=False,
                )
            ##############
            # Third ROW:
            ##############
            with gr.Row() as row_two:
                username = gr.Textbox(label="Username", placeholder="Enter your username")
                password = gr.Textbox(label="Password", type="password", placeholder="Enter your password")
                login_btn = gr.Button(value="Login")
                chat_type = gr.Dropdown(
                    label="Chat Type", choices=[
                        "Q&A with stored SQL-DB",
                        "Q&A with stored CSV/XLSX SQL-DB",
                        "RAG with stored CSV/XLSX ChromaDB",
                        "Q&A with Uploaded CSV/XLSX SQL-DB",
                        "Generic"
                    ], value="Q&A with stored SQL-DB")
                text_submit_btn = gr.Button(value="Submit Text")
                upload_btn = gr.UploadButton(
                    "📁 Upload CSV or XLSX files", file_types=['.csv'], file_count="multiple")
                clear_button = gr.ClearButton([input_txt, chatbot])
                login_status = gr.Textbox(label="Login Status", placeholder="Login status will appear here", interactive=False)
                access_token = gr.State()

            ##############
            # Process:
            ##############
            def handle_login_click(username, password):
                status, token = handle_login(username, password)
                return status, token

            def handle_text_submission(message, chat_type, access_token):
                status, response = send_message(message, chat_type, access_token)
                return status, response
            
            def handle_file_upload(file, access_token):
                return upload_file(file, access_token)
            
            def handle_file_processing(file, access_token):
                return process_file(file, access_token)

            # Bind functions to button clicks and text input submissions
            login_btn.click(fn=handle_login_click, inputs=[username, password], outputs=[login_status, access_token])
            input_txt.submit(fn=handle_text_submission, inputs=[input_txt, chat_type, access_token], outputs=[input_txt, chatbot])
            text_submit_btn.click(fn=handle_text_submission, inputs=[input_txt, chat_type, access_token], outputs=[input_txt, chatbot])
            upload_btn.upload(fn=handle_file_upload, inputs=[upload_btn, access_token], outputs=[input_txt])

            # Launch the Gradio app
            demo.launch(server_name="0.0.0.0", share=True)
