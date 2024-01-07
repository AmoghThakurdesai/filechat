from haystack.document_stores import InMemoryDocumentStore
from haystack.utils import build_pipeline, add_example_data, print_answers
from haystack.nodes import PromptNode 
from transformers import GenerationConfig
from haystack.pipelines import Pipeline
from getpass import getpass
from haystack.nodes import BM25Retriever
from haystack.nodes import PromptNode, PromptTemplate, AnswerParser
from fastapi import FastAPI
import os
from json import dumps
import pprint
from retrieval import retrieve_embeddings
from embedding import generate_embeddings

# HF_TOKEN = getpass("Enter your HuggingFace API token: ")


# while(True):
#     query = input("Enter your query: ")
#     output = pipe.run(query=query)
# # answers = output["answers"]
# # for answer in answers:
# #     print(f"Answer: {answer.answer}")
# #     print(f"Score: {answer.score}")
# #     print(f"Context: {answer.context}")
#     print()
#     pprint.pprint(output["results"])

