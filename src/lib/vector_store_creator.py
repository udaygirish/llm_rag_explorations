'''
Script to Create Vector Database from the Embeddings Generated 
- This file needs to be modified a lot
as this needs updation regarding what backend we use for embeddings
'''

import os
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from utilities.logger import logger
from tqdm import tqdm
import chromadb 
import shutil 
import yaml 

import pandas  as pd
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
        with open("src/config/data_config.yaml", "r") as file:
            self.config = yaml.safe_load(file)
        
        self.chat_config = ChatConfig()
        
        with open("src/config/pipeline_config.yaml", "r") as file:
            self.pipeline_config = yaml.safe_load(file)
        
        self.collection_name = self.pipeline_config["rag_config"]["collection_name"]
        self.top_k = self.pipeline_config["rag_config"]["top_k"]
            
        
        self.vector_store = self.config["vector_store_choice"]["vector_store"]
        self.vector_store_path = self.config["vector_store_choice"]["vector_store_path"]
        
        
        self.load_chroma_client()
    
    def load_chroma_client(self):
        self.chroma_client = chromadb.PersistentClient(
            path=self.vector_store_path)
        
        
    def _prepare_data_chromadb_injection(self, df: pd.DataFrame, file_name: str):
        """
        Prepare the data for injection into ChromaDB."""
        
        docs = []
        metadatas = []
        ids = []
        embeddings = []
        
        for index, row in tqdm(df.iterrows(), total=df.shape[0]):
            output_str = ""
            for col in df.columns:
                output_str += f"{col}: {row[col]},\n"
            response = self.chat_config.azure_openai_client.embeddings.create(
                input = output_str,
                model = self.chat_config.embedding_model_name
            )
            embeddings.append(response.data[0].embedding)
            docs.append(output_str)
            metadatas.append({"source": file_name}) 
            ids.append(f"id{index}")
        return docs, metadatas, ids, embeddings
    
    def _validate_db(self):
        """
        Validate the database.
        """
        vectordb = self.chroma_client.get_collection(name=self.collection_name)
        logger.info("=====================================")
        logger.info(f"Number of vectors in the collection: {vectordb.count()}")
        
    def run_pipeline(self, df, file_name):
        """
        Execute the below pipeline
        -> Load the Chroma Client
        -> Prepare the Data for Injection
        -> Validate the Database
        """
        self.load_chroma_client()
        self.docs, self.metadatas, self.ids, self.embeddings = self._prepare_data_chromadb_injection(df, file_name)
        self._validate_db()
        
        
    def load_faiss_client(self):
        self.faiss_client = FAISS()
