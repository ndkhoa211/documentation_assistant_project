import asyncio
import os
import ssl
from typing import Any, Dict, List


import certifi # for getting valid certificate,
# so we can attach to our HTTP request that we'll send

from dotenv import load_dotenv
from sqlalchemy.testing.suite.test_reflection import metadata

load_dotenv()


from langchain.text_splitter import RecursiveCharacterTextSplitter
# split top-down with the default order ["\n\n", "\n", " ", ""]

from langchain_chroma import Chroma # local vectorstore
from langchain_pinecone import PineconeVectorStore # cloud based vectorstore

from langchain_core.documents import Document # represent text document with metadata
# Document(page_content: str, metadata: Dict)

from langchain_openai import OpenAIEmbeddings
from langchain_tavily import TavilyCrawl, TavilyExtract, TavilyMap


from logger import (Colors,
                    log_info,
                    log_error,
                    log_warning,
                    log_header,
                    log_success)


# configure SSL context to use certifi certificates
# for making tons of requests for Tavily API
ssl_context = ssl.create_default_context(cafile=certifi.where())
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUEST_CA_BUNDLE"] = certifi.where()


embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    show_progress_bar=True, # show indexing progress
    chunk_size=50, # for rate limiting
    # number of text objects to be embedded in OpenAI at a single request
    retry_min_seconds=10,
    # in case a batch fails (sth wrong with the payload, or rate limits, most of the time the later),
    # we'll wait 'retry_min_seconds' seconds before we try to retry it
)


# local vectorstore
# chroma = Chroma(persist_directory="chroma_db", # store DB under project's cwd
#                 embedding_function=embeddings,
#                 )
# cloud based vectorstore
vectorstore = PineconeVectorStore(index_name="documentation-assistant-project-v2",
                                  embedding=embeddings,
                                  )
tavily_extract = TavilyExtract()
tavily_map = TavilyMap(max_depth=5,
                       max_breadth=20,
                       max_pages=1000,
                       )
tavily_crawl = TavilyCrawl() # a langchain tool









async def main():
    """Main async function to orchestrate the entire process."""
    log_header("DOCUMENTATION INGESTION PIPELINE")

    log_info(
        "TavilyCrawl: Starting to Crawl documentation from https://python.langchain.com/",
        Colors.PURPLE,
    )

    # Crawl the documentation site

    res = tavily_crawl.invoke({
        "url": "https://python.langchain.com/",
        "max_depth": 5, # default is 1
        # max_depth defines how far from the base url the crawler can explore
        # https://docs.tavily.com/documentation/best-practices/best-practices-crawl
        "extract_depth": "advanced",
        # advanced: retrieve more data, including table, embedded contents with higher success rate
        # but may increase the latency
        #"instructions": "content on AI agents",
    })

    all_docs = [Document(page_content=result['raw_content'],
                         metadata={"source": result['url']})
                for result in res['results']]

    log_success(
        f"TavilyCrawl: Successfully crawled {len(all_docs)} URLs from https://python.langchain.com/",
    )



if __name__ == '__main__':
    asyncio.run(main())