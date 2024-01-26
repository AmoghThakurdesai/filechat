import os
from haystack.document_stores import FAISSDocumentStore
from haystack.utils import convert_files_to_docs
from haystack.nodes.retriever.dense import EmbeddingRetriever
from haystack.utils import add_example_data
import json 

import logging

from haystack.pipelines import Pipeline

logging.basicConfig(level=logging.DEBUG)

document_store,retriever = None, None

def generate_embeddings():
# Initialize FAISS document store.
    document_store,retriever = None, None
    if(os.path.exists("faiss_document_store.db")):
        if os.path.exists('faiss_index.faiss'):
            document_store = FAISSDocumentStore.load(index_path="faiss_index.faiss")
            retriever = get_retriever(document_store=document_store)
        else:
            print("\n\n db not done embedding the docs. Delete the db file \n\n")
    else:
        document_store = FAISSDocumentStore(
                vector_dim=768,embedding_dim=768, faiss_index_factory_str="Flat")
        retriever = get_retriever(document_store=document_store)
        docs = convert_files_to_docs(dir_path="files")

        print("\n\nConverted to docs\n\n")
        document_store.write_documents(documents=docs)
        print("\n\nWritten docs docs\n\n")
        document_store.update_embeddings(retriever)   
    document_store.save(index_path = 'faiss_index.faiss')

    # Initialize embedding retriever
    


    return document_store,retriever

def get_retriever(document_store):
    if(not os.path.exists("embedding_retriever_config.json")):
        retriever = EmbeddingRetriever(
            document_store = document_store,
            use_gpu=True,
            embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1"
            )
        save_retriever_config(retriever)
    else:
        with open('embedding_retriever_config.json', 'r') as f:
            config = json.load(f)
            retriever = EmbeddingRetriever(
                        document_store = document_store,
                        use_gpu=config['use_gpu'],
                        embedding_model=config['embedding_model']
                    )
    return retriever
    


# def change_embeddings(retriever):
#     if(os.path.exists("faiss_document_store.db")):
#         if os.path.exists('faiss_index.faiss'):
#             document_store = FAISSDocumentStore.load(index_path="faiss_index.faiss")
#             document_store.update_embeddings(retriever)
#             document_store.save(index_path = 'faiss_index.faiss')
#         else:
#             print("Faiss Index doesnt exist")
#     else:
#         print("Database doesn't exist\n Creating ") 
#     return document_store


def save_retriever_config(retriever):
    # Manually create a dictionary of the parameters
    config = {
        'embedding_model': retriever.embedding_model,
        'use_gpu': retriever.use_gpu,
        # Add any other parameters you used to initialize the retriever
    }
    with open('embedding_retriever_config.json', 'w') as f:
        json.dump(config, f)


