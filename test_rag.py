# Create a RAG base pipeline which can ingest a doc
# and return a Output

import os
import sys

# Use FAISS , LangChain and build a RAG Pipeline

import faiss 
import torch

from tqdm import tqdm, trange
from transformers import AutoModelForCausalLM, AutoTokenizer , BitsAndBytesConfig
from langchain.embeddings import HuggingFaceBgeEmbeddings
import faiss 
import numpy as np
from tqdm import tqdm, trange
import torch
from lib.data_loaders import load_data
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from transformers import pipeline
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough



# Load Data
print("Loading Data")
text = load_data()
print("====================================="*3)
print("Total Text: ", text)
print("====================================="*3)
print("Loading Data Completed")

# Load embeddings
print("Downloading Embeddings")
embeddings = HuggingFaceBgeEmbeddings(model_name ="dunzhang/stella_en_1.5B_v5")
print("Downloading Embeddings Completed")

# print("Length of Text: ", len(text))    
# Create Embeddings
print("Creating Embeddings") 

splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=60)
recursive_text = splitter.split_text(text)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16
)

db = FAISS.from_texts(recursive_text, HuggingFaceBgeEmbeddings(model_name="BAAI/bge-base-en-v1.5")) #dunzhang/stella_en_1.5B_v5"))

# Load Model
print("Loading Model")
# Use Llama Model
model_name = "meta-llama/Meta-Llama-3-8B"
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map = "cuda:0", quantization_config=bnb_config)
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("Model loading and tokenization completed")

retriever = db.as_retriever(search_type="similarity",search_kwargs={"k": 5})

text_generation_pipeline = pipeline(
    model=model,
    tokenizer=tokenizer,
    task="text-generation",
    temperature=0.2,
    do_sample=True,
    repetition_penalty=1.1,
    return_full_text=True,
    max_new_tokens=400,
)

llm = HuggingFacePipeline(pipeline=text_generation_pipeline)

prompt_template = """
<|system|>
Answer the question based on your knowledge. Use the following context to help:

{context}

</s>
<|user|>
{question}
</s>
<|assistant|>

 """

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template,
)

llm_chain = prompt | llm | StrOutputParser()

retriever = db.as_retriever()

rag_chain = {"context": retriever, "question": RunnablePassthrough()} | llm_chain

question = "Where did Uday work on Computer Vision ?"

#response_llm = llm_chain.invoke({"context": "", "question": question})

# response_rag = rag_chain.invoke(question)

def terminal_chatbot():
    os.system("clear")
    while True:
        print("====================================="*3)
        print("Hi I am ChatAnything, you can ask me anything")
        question = input("You: ")
        response_rag = rag_chain.invoke(question)
        print("ChatAnything: ", response_rag)
        # Ask user to enter a key for next question
        input("Press Enter to ask another question")
        os.system("clear")
        
terminal_chatbot()