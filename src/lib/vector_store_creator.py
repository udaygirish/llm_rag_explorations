'''
Script to Create Vector Database from the Embeddings Generated 
- This file needs to be modified a lot
as this needs updation regarding what backend we use for embeddings
'''

import os
from utilities.logger import logger
from tqdm import tqdm
import chromadb 
import shutil 
import yaml 

# Import FAISS for Vector Store Creation
from langchain.vectorstores import FAISS 
from lib.chat_config import ChatConfig

tqdm.pandas()


class VectorStoreCreator:
    """Class to create a vector store from the embeddings generated.
    Planning to support multiple Vector Store Creators 
    """
    
    def __init__(self) -> None:
        """
        Initialize the instance with the file directory and load the app config.
        
        Args:
            file_directory (str): The directory path of the file to be processed.
        """
        # Load config from the config/data_config.yaml
        with open("config/data_config.yaml", "r") as file:
            self.config = yaml.safe_load(file)
        
        self.chat_config = ChatConfig()
            
        
        self.vector_store = self.config["vector_store_choice"]["vector_store"]
        self.vector_store_path = self.config["vector_store_choice"]["vector_store_path"]
    
    def load_chroma_client(self):
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.file_directory))
    
    def load_faiss_client(self):
        pass
