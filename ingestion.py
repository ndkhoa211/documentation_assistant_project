from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.document_loaders import ReadTheDocsLoader
from langchain_pinecone import PineconeVectorStore

embeddings = OpenAIEmbeddings(model="text-embedding-3-small") # same model as pinecone vectorstore


def ingest_docs():
    loader = ReadTheDocsLoader("langchain-docs/api.python.langchain.com/en/latest",
                               encoding="utf-8")

    raw_documents = loader.load()
    print(f"loaded {len(raw_documents)} documents")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    documents = text_splitter.split_documents(raw_documents)

    # iterate over the chunked documents
    for doc in documents:
        new_url = doc.metadata["source"]

        # convert Windows-style backlashes to forward slashed
        new_url = new_url.replace("\\", "/")
        new_url = new_url.replace("langchain-docs/", "")

        # remove all protocol prefixes first
        new_url = new_url.replace("https://", "").replace("http://", "")

        # add single clean https:// prefix
        new_url = "https://" + new_url.lstrip("/")

        doc.metadata.update({"source": new_url})

    print(f"Going to add {len(documents)} documents to Pinecone")

    # create vectorstore
    vectorstore = PineconeVectorStore(index_name="documentation-assistant-project",
                                      embedding=embeddings
                                      )

    # define batch size
    batch_size = 100 # too large might get pinecone upserting error

    # loop through documents in batches
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        vectorstore.add_documents(batch) # convert to embeddings and upsert to pinecone vectorstore
        print(f"Uploaded batch {i // batch_size + 1} with {len(batch)} documents")

    print("***** Loading to vectorstore done! *****")

if __name__ == "__main__":
    print("Starting ingestion")
    ingest_docs()


