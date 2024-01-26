import streamlit as st
import requests
import os
from streamlit_js_eval import streamlit_js_eval

# Set the API URL
API_URL = "http://localhost:8000"

def generate_embeddings():
    response = requests.get(f"{API_URL}/generate_embeddings")
    if response.status_code == 200:
        st.write("Embeddings generated successfully")
    else:
        st.write("Failed to generate embeddings")

def retrieve_embeddings(query):
    response = requests.get(f"{API_URL}/retrieve_embeddings/{query}")
    if response.status_code == 200:
        results = response.json()["results"]
        st.write(results)
    else:
        st.write("Failed to retrieve embeddings")

def upload_file(file):
    files = {"file": file}
    response = requests.post(f"{API_URL}/uploadfile/", files=files)
    if response.status_code == 200:
        st.write("File uploaded successfully")
    else:
        st.write("Failed to upload file")

def delete_file(file):
    response = requests.post(f"{API_URL}/deletefile/{file}")
    if response.status_code == 200:
        st.write("File deleted successfully")
        streamlit_js_eval (js_expressions="parent.window.location.reload ()")
    else:
        st.write("Failed to delete file")

def get_uploaded_files():
    response = requests.get(f"{API_URL}/uploadedfiles")
    if response.status_code == 200:
        files = response.json()["dirlist"]
        return files
    else:
        st.write("Failed to get uploaded files")
        return []

def app():
    st.title("FastAPI Frontend with Streamlit")

    # Generate embeddings
    st.warning("Make sure the embeddings are generated prior to retrieving responses.")
    if st.button("Generate Embeddings"):
        generate_embeddings()

    # Retrieve embeddings
    query = st.text_input("Enter your query")
    if st.button("Get answer"):
        retrieve_embeddings(query)

    # Upload file
    st.warning("Please avoid uploading files with extensive tabular data as it may lead to suboptimal results.")
    uploaded_file = st.file_uploader("Choose a file")
    if st.button("Upload File"):
        upload_file(uploaded_file)

    # Delete file
    files = get_uploaded_files()
    file_to_delete = st.selectbox("Select a file to delete", files)
    if st.button("Delete File"):
        delete_file(file_to_delete)

    # Display uploaded files
    st.write("Uploaded files:")
    st.write(files)

if __name__ == "__main__":
    app()
