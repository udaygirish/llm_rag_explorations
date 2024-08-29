import os 
from dotenv import load_dotenv 
import yaml
import shutil 
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from utilities.logger import logger



# Load the environment variables

if os.path.exists(".env"):
    load_dotenv()
    logger.info("Environment variables are loaded - CHAT CONFIG")
    logger.info("Stored API Credentials or URLs")


# ToDo:
# Change Imports according to what chat is needed
# Currently Importing all the existing API's and model frameworks

from openai import AzureOpenAI 
from langchain.chat_models import AzureChatOpenAI
from langchain.chat_models import ChatAnthropic 
from langchain_google_vertexai import ChatVertexAI  
from langchain_cohere import ChatCohere 
from langchain_fireworks  import ChatFireworks 
from langchain_mistralai  import ChatMistralAI
from langchain_openai import ChatOpenAI 
from langchain_huggingface import HuggingFaceEmbeddings


# For open Source models 
# ToDO: Plan to support atleast most of the Top open source models
# Configuations - Ollama, llama.cpp, Huggingface 
# Currently Using - Ollama

from langchain_ollama import ChatOllama

class ChatConfig:
    def __init__(self) -> None:
        with open("src/config/model_config.yaml") as cfg:
            config = yaml.load(cfg, Loader=yaml.FullLoader)
        
        model_config= config['model_config']
        llm_config = config['llm_config']
        self.model_name = model_config['llm_list'][model_config['llm_name']]
        self.embedding_model = model_config['embedding_model_list'][model_config['embedding_model']]
        # self.llm_tokenizer = model_config['llm_tokenizer']
        self.engine = model_config['engine_list'][model_config['engine']]
        
        self.agent_llm_system_role = llm_config[self.model_name]['agent_llm_system_role']
        self.rag_llm_system_role = llm_config[self.model_name]['rag_llm_system_role']
        self.temperature = llm_config[self.model_name]['temperature']
        self.model_engine = llm_config[self.model_name]['engine']
        
        self.load_chat_model()
    
    def load_chat_model(self):
        # ToDo:  Convert this to a Dictionary based format 
        # To use different API's for different Models based on the configuration /service
        # check lower letters only
        
        #n This will be removed in Future Currently for Experimentation
        # TODO: highlight this
        # Also open Source model currently not encrypting at OLLAMA level
        # But overall the Backend Chat API is Encrypted
        if self.engine.lower() != "ollama":
            # Have to update this for more support
            self.azure_openai_client = AzureOpenAI(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    api_version=os.getenv("OPENAI_API_VERSION"),
                    azure_endpoint=os.getenv("OPENAI_API_BASE")
                )
        else:
            model_kwargs = {'device': 'cpu'}
            encode_kwargs = {'normalize_embeddings': False}
            self.embedding_client = HuggingFaceEmbeddings(model_name=self.embedding_model, 
                                                          model_kwargs=model_kwargs,
                                                          encode_kwargs=encode_kwargs)
        if self.engine.lower() == "azurechatopenai":
            # self.azure_openai_client = AzureOpenAI(
            #     api_key=os.getenv("OPENAI_API_KEY"),
            #     api_version=os.getenv("OPENAI_API_VERSION"),
            #     azure_endpoint=os.getenv("OPENAI_API_BASE")
            # )
            self.chat_model = AzureChatOpenAI(
                openai_api_version=os.getenv("OPENAI_API_VERSION"),
                azure_deployment=self.model_name,
                model_name=self.model_name,
                temperature=self.temperature
            )
        elif self.engine.lower() == "ollama":
            # This is Assuming OLLAMA running on Same machine
            # Dev is Ongoing to Support Hugging Face and also Ollama
            # Endpoints hosted on other machines.
            self.chat_model = ChatOllama(
                model=self.model_name,
                temperature=self.temperature,
                num_predict = 1024
            )
        elif self.engine.lower() == "openai":
            self.chat_model = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        elif self.engine.lower() == "anthropic":
            self.chat_model = ChatAnthropic(
                        model=self.model_name,
                        temperature=self.temperature,
                        api_key=os.getenv("ANTHROPIC_API_KEY"),
                    )
        elif self.engine.lower() == "googleai":
            self.chat_model = ChatVertexAI(
                model=self.model_name, google_api_key=os.getenv("GOOGLE_API_KEY"))
        elif self.engine.lower() == "cohere":
            self.chat_model = ChatCohere(
                model=self.model_name, cohere_api_key=os.getenv("COHERE_API_KEY"))
        elif self.engine.lower() == "fireworks":
            self.chat_model = ChatFireworks(
                model=self.model_name, fireworks_api_key=os.getenv("FIREWORKS_API_KEY"))
        elif self.engine.lower() == "mistralai":
            self.chat_model = ChatMistralAI(
                model=self.model_name, mistralai_api_key=os.getenv("MISTRALAI_API_KEY"))    
        else:
            logger.error("No Chat Model Found - Please Select Valid Model Config in Model Config YAML @src/config")
            exit(1)
            pass 
        return self.chat_model
    
    
    
        
        
        