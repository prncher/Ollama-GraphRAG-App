import argparse
import asyncio
import os
from langchain_ollama import ChatOllama, OllamaEmbeddings
from dotenv import load_dotenv

import ollama
from sklearn.preprocessing import normalize
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j import GraphDatabase
from neo4j_graphrag.indexes import create_vector_index, drop_index_if_exists, upsert_vectors

from neo4j_graphrag.indexes import upsert_vector
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.generation.types import RagResultModel
from neo4j_graphrag.retrievers import Text2CypherRetriever
from neo4j_graphrag.schema import get_schema
from neo4j_graphrag.types import RetrieverResultItem
from langchain_neo4j import Neo4jGraph

class Application:
    def __init__(self,username,password):
        self.model = "rjmalagon/gte-qwen2-1.5b-instruct-embed-f16"
        self.URI = "neo4j://localhost:7687"
        self.user = username
        self.password = password
        self.INDEX_NAME = "your_vector_index_name"
        self.EMBEDDING_PROPERTY = "vector_embedding_property"
 

    def createVectorIndex(self):
        session = None
        driver = None
        try:
            driver = GraphDatabase.driver(self.URI, auth=(self.user, self.password))
            session = driver.session(database="northwind")

            drop_index_if_exists(driver,
                                name=self.INDEX_NAME,
                                neo4j_database="northwind")

            create_vector_index(
                driver,
                name=self.INDEX_NAME,
                label="Document",
                embedding_property=self.EMBEDDING_PROPERTY,
                dimensions=1536,
                similarity_fn="euclidean",
                neo4j_database="northwind",
                fail_if_exists=False
                )
            response = ollama.embed(model=self.model)
            print(f"Embeddings: {response.embeddings}")
            upsert_vectors(
                driver,
                ids=['1234'],
                embedding_property=self.EMBEDDING_PROPERTY,
                embeddings=[response.embeddings],
                neo4j_database="northwind",
                entity_type='NODE',
            )
            
        except Exception as e:
            print(f"Exception in createVectorIndex: {e}")
        finally:
            session.close()
            driver.close()

    def loadSchema(self):
        try:
            ollama_model = os.environ.get("OLLAMA_MODEL", "Llama3.1:8b")
            self.llm = ChatOllama(
                model=ollama_model,
                validate_model_on_init=True,
                temperature=0.8,
                num_ctx=32000,  # Large context window for complex tasks
                base_url="http://localhost:11434",
            )

            graph = Neo4jGraph(self.URI, 
                                username=self.user, 
                                password=self.password,
                                database="northwind")
            print(graph.schema)
            self.schema = graph.schema
        except Exception as e:
            print(f"Exception in loadSchema: {e}")


    def run(self, question):
        driver = GraphDatabase.driver(self.URI, auth=(self.user, self.password))
        session = driver.session(database="northwind")

        try:
            retriever = Text2CypherRetriever(
                    driver=driver,
                    llm=self.llm,
                    neo4j_schema=self.schema,
                    neo4j_database="northwind",
                    result_formatter=lambda x: RetrieverResultItem(content=x.data()))
            result = retriever.search(query_text=question)
        

            for i, item in enumerate(result.items):
                print(f"Result {i}: {item.content}")
                print(f"Metadata: {item.metadata}")
        except Exception as e:
            print(f"Exception in run: {e}")
        finally:
            driver.close()
            session.close()
    
async def main(query,ragApp):
    try:
        ragApp.run(query)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    load_dotenv()
    user = os.getenv("NEO4USER")
    paswd = os.getenv("PASSWORD")
    os.environ["USER_AGENT"] = "Ollama-RAG-Pipeline-App-Llama3.1/0.1.0 (prncher@gmail.com)"

    try:
        ragApp = Application(user,paswd)
        ragApp.createVectorIndex()
        ragApp.loadSchema()
        while True:
            query = input("Enter a nlq for northwind graph DB (or 'exit' to quit): ")
            if query.lower() == 'exit':
                break
            try:
                asyncio.run(main(query,ragApp))
            except Exception as e:
                print(f"Error: {e}")
    except Exception as e:
        print(e)


    
    