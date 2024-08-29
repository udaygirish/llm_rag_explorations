import os 
from typing import List, Tuple, Dict

import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from lib.chat_config import ChatConfig
from lib.vector_store_creator import VectorStoreCreator 
from lib.db_creator import DBCreator

import langchain

# Langchain helpers for SQL Database and SQL Queries
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

# Langchain Prompt Helpers
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from glob import glob



from operator import itemgetter
from utilities.logger import logger

# Import SQL Alchemy this should be allowed to support multiple databases
from sqlalchemy import create_engine
from langchain_community.agent_toolkits import create_sql_agent
from datetime import datetime
import yaml

# Set Langchain Debug to True
langchain.debug = True

class ChatBOT:
    
    def __init__(self) -> None:
        self.description = "Chatbot Class for API to interact with SQL Databases and RAG Models"
        with open("src/config/data_config.yaml") as cfg:
            data_config = yaml.load(cfg, Loader=yaml.FullLoader)
        
        self.sqldb_directory = data_config["data_directories"]["sqldb_directory"]
        self.uploaded_files_sqldb_directory = data_config["data_directories"]["uploaded_files_sqldb_directory"]
        self.storage_download_sqldb_directory = data_config["data_directories"]["stored_csv_xlsx_sqldb_directory"]
        self.chat_config = ChatConfig()
        self.vector_store_creator = VectorStoreCreator()
        
    def respond(self, chatbot_hist:List, message:str, chat_type:str) -> Tuple:
        """
        ChatBot Respond Function to respond to the user message based on the chat_type and app_functionality
        
        Primary Function Call for Fast API to respond to the user message
        """
        # Log Datetime in String Format MM DD YYYY HH:MM:SS
        logger.info(f"ChatBot Respond Function Called at {datetime.now().strftime('%m %d %Y %H:%M:%S')}")
        
        if chat_type == "Q&A with stored SQL-DB":
            # Load the Chat Config
            
            # Check the SQL Database Path
            if os.path.exists(self.sqldb_directory):
                db = SQLDatabase.from_uri(f"sqlite:///{self.sqldb_directory}")
                # logger.info("==== SQL Database Loaded Successfully ====")
                # logger.info("Table Names in the SQL Database")
                # logger.info(db.table_names)
                execute_query = QuerySQLDataBaseTool(db=db)
                write_query = create_sql_query_chain(self.chat_config.chat_model, db)
                
                answer_prompt = PromptTemplate.from_template(self.chat_config.agent_llm_system_role)
                answer = answer_prompt | self.chat_config.chat_model | StrOutputParser()
                chain = (
                    RunnablePassthrough.assign(query=write_query).assign(
                        result=itemgetter("query") | execute_query
                    )
                    | answer
                )
                response = chain.invoke({"question": message})
            else:
                response = "No SQL Database Found to interact with Please Create a SQL Database"
                return response, chatbot_hist, None
            
        elif chat_type == "Generic":
            prompt_message = [
                (
                    "system",
                    "This Chatbot is to answer questions generic from the Knowledge base",
                ),
                ("user", message),
            ]
            response = self.chat_config.chat_model.invoke(prompt_message)
            response = response.content
            
        elif chat_type == "Q&A with Uploaded CSV/XLSX SQL-DB" or chat_type == "Q&A with stored CSV/XLSX SQL-DB":
            if chat_type == "Q&A with Uploaded CSV/XLSX SQL-DB":
                if os.path.exists(self.uploaded_files_sqldb_directory):
                    engine = create_engine(f"sqlite:///{self.uploaded_files_sqldb_directory}")
                    db = SQLDatabase(engine=engine)
                    print(db.dialect)
                else:
                    response = "SQL DB from the uploaded csv/xlsx files does not exist. Please first upload the csv files from the chatbot."
                    return response, chatbot_hist, None
            elif chat_type == "Q&A with stored CSV/XLSX SQL-DB":
                if os.path.exists(self.storage_download_sqldb_directory):
                    engine = create_engine(f"sqlite:///{self.storage_download_sqldb_directory}")
                    db = SQLDatabase(engine=engine)
                else:
                    response = "SQL DB from the stored csv/xlsx files does not exist. Please first upload the csv files from the chatbot."
                    return response, chatbot_hist, None 
            
            # Check whether using differnt agent type makes sense or not
            agent_executor = create_sql_agent(self.chat_config.chat_model, db=db, agent_type="openai-tools",
                                              verbose=True)
            response = agent_executor.invoke({"input": message})
            response = response["output"]
            
        elif chat_type == "RAG with stored CSV/XLSX ChromaDB":
            response = self.chat_config.azure_openai_client.embeddings.create(
                input=message,
                model=self.chat_config.embedding_model
            )
            query_embeddings = response.data[0].embedding
            vector_db = self.vector_store_creator.chroma_client.get_collection(
                name=self.vector_store_creator.collection_name
            )
            rag_results = vector_db.query(query_embeddings, n_results=self.vector_store_creator.top_k)
            
            prompt = f"User's question: {message} \n\n Search results:\n {rag_results}"
            
            messages = [
                {"role": "system", "content": str(self.chat_config.rag_llm_system_role)},
                {"role": "user", "content": prompt}
            ]
            
            llm_response = self.chat_config.azure_openai_client.chat.completions.create(
                model=self.chat_config.model_name,
                messages=messages
            )
            
            response = llm_response.choices[0].message.content
            
        chatbot_hist.append((message, response))
        
        return chatbot_hist 
    
    
    
# FAST API on Top of ChatBot Class
from fastapi import FastAPI, Request, Depends, HTTPException, status
# Import CORS to allow Cross Origin Resource Sharing
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from utilities.security_helpers import Security_Helpers
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials  
from pydantic import BaseModel

app = FastAPI()
security_helpers = Security_Helpers()

# Add CORS Middleware to allow Cross Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
token_auth_scheme = HTTPBearer()

chatbot = ChatBOT()
# db_creator = DBCreator()

# Default Entry  Path - API Health Test
@app.get("/")
def read_root():
    return {"API": "ChatBot API is Running"}


# Endpoint to Generate Token
@app.post("/api/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    if not security_helpers.verify_user(username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create JWT Token
    access_token = security_helpers.create_jwt_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}





# API Endpoint to interact with the ChatBot
@app.post("/chatbot")
async def chatbot_response(request_data:Dict, token: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    """
    ChatBot API Endpoint to interact with the ChatBot
    """
    token = token.credentials
    username = security_helpers.verify_jwt_token(token)
    message = request_data.get("message")
    chat_type = request_data.get("chat_type")
    chatbot_hist = request_data.get("chatbot_hist")
    
    
    chatbot_hist = chatbot.respond(chatbot_hist, message, chat_type)
    
    return {"chatbot_hist": chatbot_hist}

# API Endpoint for Adding Data to the SQL Database
# Able to add data to the SQL Database
# @app.post("/list_data_storage/")
# async def list_data_storage(request_data : Dict):
#     """
#     API Endpoint to add data to the SQL Database
#     """
#     data_location = request_data.get("data_location")
#     # This Data URL can be used Query Storage Buckets
#     # Currently not configured but can be configured in future
#     data_url = request_data.get("data_url")
#     if data_location == "uploaded":
#         # Get the List of files from the uploaded directory
        
        
    


# Run the Fast API Server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
        
'''
{"message": "Hi How are you ?",
"chat_type":"Generic",
"chatbot_hist": []
}
'''        
