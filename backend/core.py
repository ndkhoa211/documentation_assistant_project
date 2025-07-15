from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

from langchain.chains.retrieval import create_retrieval_chain
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains.history_aware_retriever import create_history_aware_retriever

INDEX_NAME = "documentation-assistant-project"


def run_llm(
    query: str,
    chat_history: List[Dict[str, Any]] = [],
):
    # create embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # create a (vectorstore as a) retriever
    docsearch = PineconeVectorStore(
        index_name=INDEX_NAME,
        embedding=embeddings,
    )

    # create a chat object
    chat = ChatOpenAI(
        model="gpt-4.1",
        verbose=True,
        temperature=0.0,
    )

    # prompt
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

    # create a chain: send `prompt` to `chat` with a placeholder `context` (aka the relevant documents)
    stuff_documents_chain = create_stuff_documents_chain(
        chat,
        retrieval_qa_chat_prompt,
    )

    # rephrase question
    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")

    history_aware_retriever = create_history_aware_retriever(
        llm=chat,
        retriever=docsearch.as_retriever(),
        prompt=rephrase_prompt,
    )

    # create a retrieval chain
    qa = create_retrieval_chain(
        retriever=docsearch.as_retriever(),
        combine_docs_chain=stuff_documents_chain,
    )

    # invoke chain
    result = qa.invoke(
        input={
            "input": query,
            "chat_history": chat_history,
        }
    )

    # change dict's key name
    new_result = {
        "query": result["input"],
        "result": result["answer"],
        "source_documents": result["context"],
    }

    return new_result


if __name__ == "__main__":
    res = run_llm(query="What is a LangChain chain?")
    print(f"Answer: {res['answer']}")
    print("\nGrounding Documents:")
    for doc in res.get(
        "context",
        [],  # return `None` if "context" is missing
    ):
        # Each Document’s metadata typically contains both the vector‑store id and its original source
        doc_id = doc.id  # vector id
        src_path = doc.metadata.get("source")  # e.g. file path / URL

        print(f"ID: {doc_id}\tSource: {src_path}")
