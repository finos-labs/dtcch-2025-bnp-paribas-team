import gradio as gr
import tools
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore
from pipelines import indexing_pipeline, rag_pipeline
from pathlib import Path

#Initialize DocumentStore, then index and load documents from local dir
document_store = InMemoryDocumentStore()
indexing_pipeline(input_dir='data/documents', document_store=document_store)

print(list(Path('data/documents').glob("**/*.*")))
print(document_store.count_documents())

#initialize RAG pipeline
rag_pipe = rag_pipeline(document_store)

tool_msg = None
messages = [
    ChatMessage.from_system(
        "Use the tool that you're provided with. Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."
    )
]

def chatbot_with_tc(message, history):
    global rag_pipe
    tool_msg = tools.rag_pipeline_func(ChatMessage.from_user(message).text, rag_pipe)
    return tool_msg["reply"]


drop_down_options = ['META','TSLA','OREX','RUM','AZUL4','IHRT','TBMC','WAIR','SPHINX','PLTR','Other']

# Add custom CSS to change background color
css = """
body {
  background-color: #d6ebe2; /* Change to your desired background color */
}

.gradio-container {
  background-color: #d6ebe2; /* Change to your desired background color */
}

#markdown-component {
  background-color: #d6ebe2; /* Change to your desired background color */
  font-weight: bold; /* Makes the text bold */
  font-size: 50px; /* Adjusts the height of the text , not working :/*/
  text-align:center !important;
}

.gradio-textbox {
  background-color: #dff5f9; /* Change to your desired background color */
}

.gradio-dropdown {
  background-color: #dff5f9; /* Change to your desired background color */
}

"""
demo = gr.Blocks(css = css)
with demo:
    gr.Markdown("# Action Eye", elem_id="markdown-component")
    # text_box = gr.Textbox(label="Ask Me About a Corporate Action Event")
    ticker_option = gr.Dropdown(multiselect =False, label = "Select or Enter a Ticker Symbol if Known",choices=drop_down_options, value = None)
    optional_text_box = gr.Textbox(label="Enter Ticker", visible = False)
    # submit_button = gr.Button("Submit")
    # output_text = gr.Text(label="Here you go!")


    def toggle_input(ticker_option):
        return gr.update(visible=(ticker_option == "Other"))

    def chatbot_with_tc(query, history, ticker_options, optional_text_box):
        # Use the options variable here
        ticker = None
        if ticker_options == "Other":
            ticker = optional_text_box
        else:
            ticker = ticker_options
        tool_msg = tools.rag_pipeline_func(query, rag_pipe, ticker)
        return tool_msg["reply"]

    ticker_option.change(toggle_input, inputs = [ticker_option], outputs=[optional_text_box])
    # submit_button.click(chatbot_with_tc, inputs=[text_box, ticker_option, optional_text_box], outputs=output_text)
    chat = gr.ChatInterface(title="Chat with Action Eye",fn=chatbot_with_tc,additional_inputs=[ticker_option,optional_text_box])

if __name__ == "__main__":
    demo.launch()

