from haystack import Pipeline, Document
from haystack.dataclasses import ChatMessage
from haystack.components.writers import DocumentWriter
from haystack.components.converters import MarkdownToDocument, PyPDFToDocument, TextFileToDocument
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.routers import FileTypeRouter
from haystack.components.joiners import DocumentJoiner
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack_api import get_doc_embedder, get_text_embedder, get_chat
from pathlib import Path
import pickle

def indexing_pipeline(input_dir,document_store):
    #docs = [Document(content=doc["content"], meta=doc["meta"]) for doc in documents]
    #load metadata
    with open("data/meta.pkl","rb") as file:
        meta = pickle.load(file)
    #initialize pipeline components
    file_type_router = FileTypeRouter(mime_types=["text/plain","application/json"])
    text_file_converter = TextFileToDocument()
    text_file_converter2 = TextFileToDocument()
    document_joiner = DocumentJoiner()
    document_cleaner = DocumentCleaner()
    document_splitter = DocumentSplitter(split_by="word", split_length=70, split_overlap=10)
    document_embedder = get_doc_embedder()
    document_writer = DocumentWriter(document_store)

    #set up pipeline
    preprocessing_pipeline = Pipeline()
    preprocessing_pipeline.add_component(instance=file_type_router, name="file_type_router")
    preprocessing_pipeline.add_component(instance=text_file_converter, name="text_file_converter")
    preprocessing_pipeline.add_component(instance=text_file_converter2, name="text_file_converter2")
    preprocessing_pipeline.add_component(instance=document_joiner, name="document_joiner")
    preprocessing_pipeline.add_component(instance=document_cleaner, name="document_cleaner")
    preprocessing_pipeline.add_component(instance=document_splitter, name="document_splitter")
    preprocessing_pipeline.add_component(instance=document_embedder, name="document_embedder")
    preprocessing_pipeline.add_component(instance=document_writer, name="document_writer")

    #connect pipeline
    preprocessing_pipeline.connect("file_type_router.text/plain", "text_file_converter.sources")
    preprocessing_pipeline.connect("file_type_router.application/json", "text_file_converter2.sources")
    preprocessing_pipeline.connect("text_file_converter", "document_joiner")
    preprocessing_pipeline.connect("text_file_converter2", "document_joiner")
    preprocessing_pipeline.connect("document_joiner", "document_cleaner")
    preprocessing_pipeline.connect("document_cleaner", "document_splitter")
    preprocessing_pipeline.connect("document_splitter", "document_embedder")
    preprocessing_pipeline.connect("document_embedder", "document_writer")
    #run pipeline
    preprocessing_pipeline.run({"file_type_router": {"sources": list(Path(input_dir).glob("**/*")),"meta":meta}})

def rag_pipeline(document_store):
    template = [
        ChatMessage.from_system(
            """
    You are a conversational agent providing corporate action search, analysis and summarization capabilities for banking clients.
    Provide complete, accurate answers to user questions based on the given context.
    Do not give any information in your response which says what context you used.
    
    Context:
    {% for document in documents %}
        {{ document.content }}
    {% endfor %}
    
    Question: {{ question }}
    Answer:
    """
        )
    ]

    template_B = [
        ChatMessage.from_system(
            """
            Please use the context available below to answer the query. If the necessary information isn't provided, feel free to conduct your own search to gather details. Aim for slightly detailed responses where relevant, and use bullet points if it helps clarify the answer. Keep it concise, avoid being overly verbose, but ensure the response is informative and clear.
            
            Context:
            {% for document in documents %}
            {{ document.content }}
            {% endfor %}
            
            Do not give any information in your response which says what context you used.
            
            Question: {{ question }}
            Answer:
            """
        )
    ]



    rag_pipe = Pipeline()
    #Initialize pipeline components
    rag_pipe.add_component("embedder", get_text_embedder())
    rag_pipe.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
    rag_pipe.add_component("prompt_builder", ChatPromptBuilder(template=template_B))
    rag_pipe.add_component("llm", get_chat())

    #connect components
    rag_pipe.connect("embedder.embedding", "retriever.query_embedding")
    rag_pipe.connect("retriever", "prompt_builder.documents")
    rag_pipe.connect("prompt_builder.prompt", "llm.messages")
    return rag_pipe
