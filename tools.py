from haystack.tools import Tool

def rag_pipeline_func(query: str, rag_pipe, ticker=None):
    if ticker is None:
        result = rag_pipe.run({"embedder": {"text": query}, "prompt_builder": {"question": query}})
    else:
        result = rag_pipe.run({"embedder": {"text": query}, "prompt_builder": {"question": query}, "retriever": {"filters": {"field": "meta.ticker", "operator": "==", "value": ticker}}})
    return {"reply": result["llm"]["replies"][0].text}


rag_pipe_params = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "The query to use in the search. Infer this from the user's message. It should be a question or a statement",
        }
    },
    "required": ["query"],
}

rag_pipeline_tool = Tool(
    name="rag_pipeline_tool",
    description="Augment the response with data from DocumentStore",
    parameters=rag_pipe_params,
    function=rag_pipeline_func,
)