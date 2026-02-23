import os
import chromadb
from chromadb.utils import embedding_functions
from sqlalchemy import create_engine, inspect

from dotenv import load_dotenv

load_dotenv()

class SchemaVectorStorage:
    def __init__(self):

        #initialize a client to store the vectors in local
        self.chroma_client = chromadb.PersistentClient(path = "./chroma_db") 

        # Setup the embedding model using the embedding function this is used to will convert the text into vectors
        self.embedding = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

        #Create a collection with the embedding function
        self.collection = self.chroma_client.get_or_create_collection(
            embedding_function= self.embedding,
            name="marketplace_schema"
            )

    def index_schema(self):
        # Read Postgresql schema and store in ChromaDB
        print("Indexing the schema...")
        DATABASE_URL = os.getenv("DATABASE_URL")
        #Connect the DB and assign an inspector to gather the table names
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        documents = []
        metadatas = []
        ids = []

        for table in table_names:
            columns = inspector.get_columns(table)

            col_desc = ", ".join([f"{col['name']} ({col['type']})" for col in columns])
            text_representation = f"Table name: {table}\nColumns: {col_desc}"

            documents.append(text_representation)
            metadatas.append({"Table name":table})
            ids.append(table)

        #Add the document,metadata and Id to the chroma collection
        self.collection.upsert(
            ids=ids,
            metadatas=metadatas,
            documents=documents
        )
        print(f"Indexed {len(table_names)} tables into ChromaDB")
    
    def get_relevant_tables(self, query: str, number_of_results: int=2):
        # Takes a user question and returns top n_results
        results = self.collection.query( 
            query_texts=[query],
            n_results= number_of_results
        )

        relevant_tables = []
        for i,doc in enumerate(results["documents"][0]):
            table_name = results["metadatas"][0][i]["Table name"]
            relevant_tables.append({
                "table_name":table_name,
                "schema_text" : doc
            }
            )
        return relevant_tables
    
#Testing
# if __name__ == "__main__":
#     # Initialize
#     vector_store = SchemaVectorStorage()

#     # Step 1: Index the schema (Run this once)
#     vector_store.index_schema()

#     query = input("Enter the prompt related to the database\n")
#     print(f"\n Query: {query}")

#     results = vector_store.get_relevant_tables(query)
    
#     print("Most Relevant Tables Found:")
#     for res in results:
#         print(f" - {res['table_name']}")

