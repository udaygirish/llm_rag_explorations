import plotly.express as px
from shiny import App, ui, render
from shinywidgets import render_widget, output_widget

# Define the UI
app_ui = ui.page_fluid(
    ui.tags.head(ui.tags.title("ChatAnything")),
    ui.tags.style("body {color: #D51900; background-color: #FFFFFF;}"),
    
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_select("model_var", "Select Model", choices=["llama3", "llama2", "gpt-4o", "gemini-1_5"]),
            ui.input_select("embedding_var", "Select Embedding Model", choices=["vertexai_embedder", "gpt_embedder", "llama_embedder", "nomic_embedder"]),
            ui.input_slider("temperature", "Select Creativity", min=0, max=1, step=0.1, value=0.5),
            ui.input_select("use_rag", "Use RAG Pipeline", choices=["Yes", "No"]),
            ui.input_text("data_location", "Enter Data Location"),
            ui.input_text("api_key", "Enter API Key"),
            ui.input_action_button("authorize", "Authorize"),
            ui.input_action_button("rel_pipeline", "Reload Pipeline", style="color: #D51900; background-color: #FFFFFF;")
        ),
        ui.panel_main(
            ui.navset_card_underline(
                ui.nav_panel("Text", ui.output_text_verbatim("text_panel")),
                ui.nav_panel("Plots", output_widget("plot_panel")),
                ui.nav_panel("Retrieved Data", ui.output_table("data_panel"))
            ),
            ui.input_text_area("question", "Ask a question ?", width="100%", autocomplete="on", spellcheck="true", autoresize=True, placeholder="what are the documents about? Generate summaries"),
            ui.input_action_button("send", "Send", style="color: #D51900; background-color: #FFFFFF;")
        )
    )
)

# Define server logic
def server(input, output, session):
    @output
    @render.text
    def text_panel():
        return "Testing Text Panel"
    
    @output
    @render_widget
    def plot_panel():
        fig = px.histogram(px.data.tips(), x="total_bill", y="tip", nbins=10)
        return fig
    
    @output
    @render.table
    def data_panel():
        return px.data.tips()

# Create the Shiny app
app = App(app_ui, server)

# Run the app
app.run()
