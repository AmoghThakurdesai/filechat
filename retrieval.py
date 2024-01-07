
def retrieve_embeddings(document_store, retriever,query):
    print("\n\n\n\n retrieve process started \n\n\n")
    results = retriever.retrieve(query)
    print("\n\n\n\n retrieve process returned \n\n\n")
    return results