import os 
import sys 

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings import OpenAIEmbeddings 

# Not used right now but this wwill be extended 

class EmbeddingModels:
    def __init__(self, model_name: str, embedding_model_name: str) -> None:
        self.model_name = model_name
        self.embedding_model_name = embedding_model_name

    def load_embedding_models(self):
        if self.embedding_model_name == "HuggingFace":
            self.embedding_model = HuggingFaceEmbeddings(model_name=self.model_name)
        elif self.embedding_model_name == "OpenAI":
            self.embedding_model = OpenAIEmbeddings(model_name=self.model_name)
        else:
            print("Invalid Embedding Model Name")
            sys.exit(1)
        return self.embedding_model