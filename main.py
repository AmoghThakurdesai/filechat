from fastapi import FastAPI,UploadFile,File
from fastapi.responses import HTMLResponse,FileResponse
from embedding import generate_embeddings
from retrieval import retrieve_embeddings
from haystack.pipelines import Pipeline
from haystack.nodes import PromptNode,PromptTemplate
from haystack.schema import Document
from fastapi.staticfiles import  StaticFiles
from haystack.nodes.file_converter.pdf_xpdf import PDFToTextConverter
from haystack.utils import convert_files_to_docs
import json
import logging
import uvicorn
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


logging.basicConfig(level=logging.DEBUG)
load_dotenv(override=True)
# Generate embeddings
document_store, retriever = None,None


origins = [
    "http://127.0.0.1:8000",  # Allow this origin
    # Add more origins if needed
]

app = FastAPI()
app.mount('/static',StaticFiles(directory="static"),name='static')
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



pipe = Pipeline()
HF_TOKEN = os.getenv('HF_TOKEN')

if not HF_TOKEN:
  raise Exception("Please set your HuggingFace API token as an environment variable: export HF_API_TOKEN=your_token(linux)")



qa_template = PromptTemplate(prompt=
  """[INST] Using the information contained in the context, answer the question(in a maximum of 10 sentences).
  If the answer cannot be deduced from the context, answer \"I don't know.\"
  Context: {join(documents)};
  Question: {query}
  [/INST]""")

# Using a dictionary
pn = PromptNode(model_name_or_path="mistralai/Mixtral-8x7B-Instruct-v0.1",
                max_length=10000,
                default_prompt_template=qa_template,
                model_kwargs={"model_max_length": 32000},
                api_key=HF_TOKEN
)

@app.get("/")
def home():
    return FileResponse("index.html")


@app.get("/generate_embeddings")
def generate():
    global document_store
    global retriever
     
    document_store,retriever = generate_embeddings()
    pipe.add_node(component=retriever, name="ESRetriever", inputs=["Query"])
    pipe.add_node(component=pn, name="prompt_node", inputs=["ESRetriever"])
           
    return {"message": "Embeddings generated successfully"}

@app.get("/retrieve_embeddings/{query}")
def retrieve(query: str):
    if retriever:
        results = pipe.run(query=query)
        print(f"\n\n\n\nReturned results from retriever\n\n\n\n\n\n")
        return {"results":results["results"][0]}
    else:
        return {"message": "Didnt generate embeddings. Generate embeddings first"}
        
@app.post('/uploadfile/')
async def create_upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    if document_store:
        file_location = f"files/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(contents)
        

        docs = convert_files_to_docs(dir_path=file_location)

        print("\n\nConverted to docs\n\n")
        document_store.write_documents(documents=docs)
        print("\n\nWritten docs docs\n\n")
        document_store.update_embeddings(retriever)
        print("\n\nUpdated Embeddings\n\n")
        document_store.save("faiss_index.faiss")
        
        return {"filename":file.filename,"message":"Embeddings updated"}
    else:
        return {"message": "Generate embeddings first"}
    


def load_retriever_config():
    with open('embedding_retriever_config.json', 'r') as f:
        config = json.load(f)
    return config

if __name__=="__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)
    
