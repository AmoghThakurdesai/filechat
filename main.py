from fastapi import FastAPI,UploadFile,File
from fastapi.responses import HTMLResponse,FileResponse
from embedding import generate_embeddings
from retrieval import retrieve_embeddings
from haystack.pipelines import Pipeline
from haystack.nodes import PromptNode,PromptTemplate
from haystack.schema import Document
from fastapi.staticfiles import  StaticFiles
from haystack.nodes.file_converter.pdf_xpdf import PDFToTextConverter
from haystack.utils.preprocessing import convert_files_to_docs
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

# the convert file to docs in upload isnt working correctly we need to fix that one
document_store, retriever = None,None
present = False

origins = [
    "http://127.0.0.1:8000",  # Allow this origin
    # Add more origins if needed
]

app = FastAPI()
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
    global present
    
    document_store,retriever = generate_embeddings()
    if not pipe.get_node("ESRetriever"):
        pipe.add_node(component=retriever, name="ESRetriever", inputs=["Query"])
    if not pipe.get_node("prompt_node"):
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
        
#TODO: optimization potential here if needed
@app.post('/uploadfile/')
async def create_upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    print(contents)
    if document_store:
        file_location = f"files/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(contents)
        
        print(contents)
        docs = convert_files_to_docs(dir_path="files")

        print("\n\nConverted to docs\n\n")
        print(docs)
        document_store.write_documents(documents=docs)
        print(f"\n\nWritten docs {docs}\n\n")

        # Store the document id and the title of the file in a JSON file
        document_store.update_embeddings(retriever)
        print("\n\nUpdated Embeddings\n\n")
        document_store.save("faiss_index.faiss")

        print("these are the docs\n\n\n\n")
        documents = document_store.get_all_documents()
        print(documents)
# Now you can access the documents' content and embedding
        
        
        return {"filename":file.filename,"message":"Embeddings updated"}
    else:
        return {"message": "Generate embeddings first"}

@app.get("/uploadedfiles")  
def get_uploaded_files():
    path = "files"
    dir_list = os.listdir(path)
    print("Files and directories in '", path, "' :")
    print(dir_list)
    return {"dirlist":dir_list}

@app.post("/deletefile/{file}")
def delete_file(file: str):
    print("\n\nBefore Deletion\n\n")
    documents = document_store.get_all_documents()
    print(documents)
    document_store.delete_documents(filters={"name":[file]})
    document_store.update_embeddings(retriever)
    document_store.save("faiss_index.faiss")
    print("\n\nAfter Deletion\n\n")
    os.remove(f"files/{file}")

    return {"deletedfile":file}

def load_retriever_config():
    with open('embedding_retriever_config.json', 'r') as f:
        config = json.load(f)
    return config

if __name__=="__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)
    
