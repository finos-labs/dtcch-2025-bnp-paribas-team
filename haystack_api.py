from haystack.dataclasses import ChatMessage
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret
from haystack.components.embedders import OpenAITextEmbedder, OpenAIDocumentEmbedder
import requests
from haystack import Document
from dotenv import load_dotenv
import os

#Get prod token from https://coding.analytics.cib.echonet/
#Go to OpenAIChatGenerator definition and add http_client=DefaultHttpxClient(verify=False) in line 152 to fix ssl error
#Go to OpenAITextEmbedder definition and add http_client=DefaultHttpxClient(verify=False) in line 103 to fix ssl error
#Go to OpenAIDocumentEmbedder definition and add http_client=DefaultHttpxClient(verify=False) in line 121 to fix ssl error
#Add from openai import DefaultHttpxClient to all 3 objects listed above

load_dotenv()
api_url = os.getenv("API_URL_PROD")
api_url_dev = os.getenv("API_URL_DEV")
api_key=os.getenv("API_TOKEN")
llm_model=os.getenv("LLM_MODEL")
embed_model=os.getenv("EMBEDDER_MODEl")
token = Secret.from_token(api_key)

def get_dev_token():
    url = os.getenv("AUTH_URL")
    data = {"grant_type": "client_credentials"}
    auth = (os.getenv("AUTH_USERNAME"), os.getenv("AUTH_PASSWORD"))
    response = requests.post(url, data=data, auth=auth)
    token = response.json()['access_token']
    return(token)

token_dev = Secret.from_token(get_dev_token())

def get_chat():
    chat_client = OpenAIChatGenerator(api_base_url=api_url,
                                      api_key=token, model=llm_model)
    return(chat_client)

def get_text_embedder():
    embedder = OpenAITextEmbedder(api_key=token_dev, api_base_url=api_url_dev,model=embed_model)
    return(embedder)

def get_doc_embedder():
    embedder = OpenAIDocumentEmbedder(api_key=token_dev, api_base_url=api_url_dev,model=embed_model)
    return(embedder)



### TESTS ###
def test_chat():
    chat_client = get_chat()
    response = chat_client.run(
        [ChatMessage.from_user("What's Natural Language Processing? Be brief.")]
    )
    return(response)

def test_text_embedder():
    embedder = get_text_embedder()
    embeddings = embedder.run('Hello World!')
    return(embeddings)

def test_doc_embedder():
    doc = Document(content="some text",meta={"title": "relevant title", "page number": 18})
    embedder = get_doc_embedder()
    docs_w_embeddings = embedder.run(documents=[doc])["documents"]
    return(docs_w_embeddings)

if __name__ == "__main__":
    print(test_text_embedder())