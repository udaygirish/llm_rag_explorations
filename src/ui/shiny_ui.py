import plotly.express as px
from shiny import App, ui, render, reactive, run_app
from shinywidgets import render_widget, output_widget
import requests

# Define the URL of the FastAPI server
FASTAPI_URL = "http://localhost:8003"

# Define the UI
app_ui = ui.page_fluid(
    ui.tags.head(ui.tags.title("ChatAnything")),
    ui.tags.style("body {color: #D51900; background-color: #FFFFFF;}"),
    
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_select("chat_type", "Select Chat Type", choices=[
                "Q&A with stored SQL-DB",
                "Generic",
                "Q&A with Uploaded CSV/XLSX SQL-DB",
                "Q&A with stored CSV/XLSX SQL-DB",
                "RAG with stored CSV/XLSX ChromaDB"
            ]),
            ui.input_text("username", "Username"),
            ui.input_password("password", "Password"),
            ui.input_action_button("login", "Login"),
            ui.output_text("login_status")
        ),
        ui.panel_main(
            ui.navset_card_underline(
                ui.nav_panel("Chat History", ui.output_code("chat_history_render")),
                ui.nav_panel("Plots", output_widget("plot_panel")),
                ui.nav_panel("Retrieved Data", ui.output_table("data_panel"))
            ),
            ui.input_text_area("question", "Ask a question", width="100%", autocomplete="on", spellcheck="true", autoresize=True, placeholder="What would you like to know?"),
            ui.input_action_button("send", "Send", style="color: #D51900; background-color: #FFFFFF;")
        )
    )
)

# Define server logic
def server(input, output, session):
    chat_history = []
    access_token = None
    
    login_status_output = reactive.Value("Not logged in")
    
    chat_history_output = reactive.Value("Please Enter a Question")
    
    @output
    @render.text
    def login_status():
        return login_status_output()
    
    @output
    @render.code
    def chat_history_render():
        return chat_history_output()
    
    @output
    @render_widget
    def plot_panel():
        fig = px.histogram(px.data.tips(), x="total_bill", y="tip", nbins=10)
        return fig
    
    @output
    @render.table
    def data_panel():
        return px.data.tips()
    
    @reactive.Effect
    @reactive.event(input.login)
    def handle_login():
        nonlocal access_token
        if input.login() is None:
            return
        username = input.username()
        password = input.password()
        response = requests.post(f"{FASTAPI_URL}/api/token", data={"username": username, "password": password})
        if response.status_code == 200:
            access_token = response.json()["access_token"]
            ui.notification_show("Login Success", type="success")
            login_status_output.set("Logged in")
        else:
            ui.notification_show("Login failed", type="error")
    
    @reactive.Effect
    @reactive.event(input.send)
    def handle_send():
        if input.send() is None:
            return
        
        nonlocal chat_history 
        if access_token is None:
            ui.notification_show("Please login first", type="warning")
            return
        
        user_message = input.question()
        chat_type = input.chat_type()
        
        if user_message:
            payload = {
                "message": user_message,
                "chat_type": chat_type,
                "chatbot_hist": chat_history
            }
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            try:
                response = requests.post(f"{FASTAPI_URL}/chatbot", json=payload, headers=headers)
                if response.status_code == 200:
                    response_data = response.json()
                    chat_history = response_data.get("chatbot_hist", [])
                    output_text = chat_history[-1][1]

                    # Format text for HTML
                    formatted_output_text = "<br>".join([f"{message[0]}: {message[1]}" for message in chat_history])
                    
                    chat_history_output.set(formatted_output_text)
                else:
                    ui.notification_show(f"Error: {response.status_code} - {response.text}", type="error")
            except Exception as e:
                ui.notification_show(f"Error: Failed to communicate with the API - {str(e)}", type="error")
            
# Create the Shiny app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    run_app(app, host="0.0.0.0", port=8004)
