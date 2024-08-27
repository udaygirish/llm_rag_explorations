# All About Data!

#### Data is the crucial part for any RAG/LLM based pipeline. Especially while dealing with data at scales and building similarity search based pipelines we need to do efficient queries. For doing efficient queries we need efficient databases and their internal optimized architecture.


This below content covers important information regarding 

1. Data Formats - This repo plans to utilize
2. Databases
3. Vector Stores for similarity Search
4. Concerns around Data


**Data Formats:**

With the help of unstructured.io and some custom functionality from Pandas. 

We support the below features.

1. CSV, .xslx (Not Workbooks - Only loads first page for now) - loading content as Table, Dataframe - Pandas, SQL DB (SQLlite3), Textual Representation for LLM Chunking
2. DOC, DOCX, PDF - Loading Pure Textual Data from Docs / Multiple Documents
3. JPEG, PNG , JPG - Loading Text from Images using OCR
4. XML, HTML - Basic Text extraction after removal of tags

Futher we also have helper function which runs on CSV to check for specific websites and query data. These helper function should be updated according to the usage.

#### Databases in RAG Pipelines or while dealing with LLMs involve two types

1. Storage Databases
2. Vector Stores

**Storage Databases:**  Storage Databases are required to hold documents which means rows or chunked information for Retrieval purposes to pass a context. They also serve as the backend for generating embeddings and saving in the vector store.

Some of the famous ones are:

1. Cassandra
2. Elastic Search
3. Google BigTable
4. MongoDB
5. Neo4j
6. Postgre SQL
7. SQL (SQLAlchemy)
8. Kafka

These databases can hold different types varying from Structured to Unstructured, JSON format to Tabular Format, Graph format which is used for Knowledge Graph Purposes as we see in Neo4j.


**Vector Stores:**

Most common ways to store and search unstructured data is to transform the data into Embeddings which are a bit complex representation of the text. This process of Embedding creation can be done by traditional methods in Machine learning such as TF-IDF and Deep learning Approaches like Simple Feature based Networks trained end to end and further removed the classification head or a couple of layers. Ideally we can also leverage using Large Models such as BART or some modified versions of GPT or Attention based architectures. 

So the query process is to embed and store all the embedding vectors in a Store/Database, then at query time embed the query and retrieve the closest/similar vectors. 

Ideally this should be scalable and can require differnt sort of search strategy. This process is handled by some of the most well known Vector Databases.

Some of the famous ones are:

1. ChromaDB
2. FAISS
3. Pinecone
4. Lance
5. HNSWLIB but might need a addition index db

There are many third party vector stores in the commercial and Open source market.
