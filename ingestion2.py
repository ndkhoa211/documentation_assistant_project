import asyncio
import os
import ssl
from typing import Any, Dict, List


import certifi # for getting valid certificate,
# so we can attach to our HTTP request that we'll send

from dotenv import load_dotenv

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
    show_progress_bar=False, # show indexing progress
    chunk_size=50, # for rate limiting
    # number of text objects to be embedded in OpenAI at a single request
    retry_min_seconds=30,
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
tavily_extract = TavilyExtract() # a langchain tool
tavily_map = TavilyMap(max_depth=5,
                       max_breadth=100,
                       limit=500,
                       categories=["Documentation"],
                       ) # a langchain tool
tavily_crawl = TavilyCrawl() # a langchain tool


def chunk_urls(urls: List[str], chunk_size: int = 3) -> List[List[str]]:
    """Split URLs into chunks of specified size."""
    chunks = []
    for i in range(0, len(urls), chunk_size):
        chunk = urls[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

async def extract_batch(urls: List[str], # a batch
                        batch_num: int # for logging
                        ) -> List[Dict[str, Any]]:
    """Extract documents from a batch of URLs."""
    try:
        log_info(f"🔄 TavilyExtract: Processing batch {batch_num} with {len(urls)} URLs",
                 Colors.BLUE,
                 )
        docs = await tavily_extract.ainvoke(input={"urls": urls,
                                                   "extract_depth": "advanced"})
        extracted_docs_count = len(docs.get("results", []))
        if extracted_docs_count > 0:
            log_success(
                f"✅ TavilyExtract: Completed batch {batch_num} - extracted {extracted_docs_count} documents"
            )
        else:
            log_error(
                f"❌ TavilyExtract: Batch {batch_num} failed to extract any documents, {docs}"
            )
        return docs
    except Exception as e:
        log_error(f"❌ TavilyExtract: Failed to extract batch {batch_num} - {e}")
        return []



# concurrently extract all the urls
async def async_extract(url_batches: List[List[str]]):
    log_header("⚙️ DOCUMENT EXTRACTION PHASE ⚙️")
    log_info(
        f"🔧 TavilyExtract: Starting concurrent extraction of {len(url_batches)} batches of URLs",
        Colors.DARKCYAN,
    )

    # Process batches concurrently
    tasks = [extract_batch(batch, i + 1) for i, batch in enumerate(url_batches)]
    batch_results = await asyncio.gather(*tasks, return_exceptions=True)

    # filter out exceptions and flatten results
    all_extracted = []
    failed_batches = 0
    for batch_result in batch_results:
        if isinstance(batch_result, Exception):
            log_error(f"❌ TavilyExtract: Batch {batch_result} failed with exception")
            failed_batches += 1
        else:
            for extracted_page in batch_result["results"]: # type: ignore
                document = Document(
                    page_content=extracted_page["raw_content"],
                    metadata={"source": extracted_page["url"]},
                )
                all_extracted.append(document)

    log_success(
        f"✅ TavilyExtract: Extraction complete: Total pages extracted: {len(all_extracted)}"
    )

    if failed_batches > 0:
        log_warning(f"⚠️ TavilyExtract: {failed_batches} batches failed during extraction")

    return all_extracted


# using TavilyCrawl to scrape contents
# async def main():
#     """Main async function to orchestrate the entire process."""
#     log_header("DOCUMENTATION INGESTION PIPELINE")
#
#     log_info(
#         "TavilyCrawl: Starting to Crawl documentation from https://python.langchain.com/",
#         Colors.PURPLE,
#     )
#
#     # Crawl the documentation site
#
#     res = tavily_crawl.invoke({
#         "url": "https://python.langchain.com/",
#         "max_depth": 5, # default is 1
#         # max_depth defines how far from the base url the crawler can explore
#         # https://docs.tavily.com/documentation/best-practices/best-practices-crawl
#         "extract_depth": "advanced",
#         # advanced: retrieve more data, including table, embedded contents with higher success rate
#         # but may increase the latency
#         #"instructions": "content on AI agents",
#     })
#
#     all_docs = [Document(page_content=result['raw_content'],
#                          metadata={"source": result['url']})
#                 for result in res['results']]
#
#     log_success(
#         f"TavilyCrawl: Successfully crawled {len(all_docs)} URLs from https://python.langchain.com/",
#     )

async def index_documents_async(documents: List[Document],
                               batch_size: int = 50):
    """Process documents in batches asynchronously."""
    log_header("⚙️ VECTOR STORAGE PHASE ⚙️")
    log_info(
        f"📦 VectorStore Indexing: Preparing to add {len(documents)} documents to vector store",
        Colors.DARKCYAN,
    )


    # Create batches
    batches = [
        documents[i: i + batch_size] for i in range(0, len(documents), batch_size)
    ]
    log_info(
        f"📦 VectorStore Indexing: Split into {len(batches)} batches of {batch_size} documents each"
    )

    # Process all batches concurrently
    async def add_batch(batch: List[Document],
                        batch_num: int):
        try:
            await vectorstore.aadd_documents(batch)
            log_success(
                f"VectorStore Indexing: Successfully added batch {batch_num}/{len(batches)} ({len(batch)} documents)"
            )
        except Exception as e:
            log_error(f"VectorStore Indexing: Failed to add batch {batch_num} - {e}")
            return False
        return True

    # Process batches concurrently
    tasks = [add_batch(batch, i + 1) for i, batch in enumerate(batches)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Count successful batches
    successful = sum(1 for result in results if result is True)

    if successful == len(batches):
        log_success(
            f"VectorStore Indexing: All batches processed successfully! ({successful}/{len(batches)})"
        )
    else:
        log_warning(
            f"VectorStore Indexing: Processed {successful}/{len(batches)} batches successfully"
        )









# using TavilyMap & TavilyExtract to get more control of scraping
async def main():
    """Main async function to orchestrate the entire process."""

    ##### 1. Website discovery with TavilyMap
    #####    Input: url site
    #####    Output: list of documentation urls
    log_header("⚙️ DOCUMENTATION INGESTION PIPELINE ⚙️")

    log_info(
        "🗺️ TavilyMap: Starting to map documentation structure from https://python.langchain.com/",
        Colors.PURPLE,
    )

    # invoke the langchain tool tavily_map
    site_map = tavily_map.invoke("https://python.langchain.com/")
    #site_map = tavily_map.invoke("https://python.langchain.com/docs/")
    #site_map = tavily_map.invoke("https://python.langchain.com/docs/concepts/")

    log_success(
        f"✅ TavilyMap: Successfully mapped {len(site_map['results'])} URLs from https://python.langchain.com/",
    )

    ##### 2. URL batching
    #####    Input: list of urls
    #####    Output: list of batches of urls
    url_batches = chunk_urls(site_map['results'],
                             chunk_size=20 # batches of 20
                             )

    log_info(f"📦 URLs Processing: Split {len(site_map['results'])} URLs into {len(url_batches)} batches",
             Colors.BLUE,
             )



    ##### 3. Content Extraction with TavilyExtract
    #####    Input: list of batches of urls
    #####    Process: concurrent extraction from web pages
    #####    Output: clean, parsed content
    all_docs = await async_extract(url_batches)




    ##### 4. Chunking the Langchain documentation
    log_header("⚙️ DOCUMENTATION CHUNKING PHASE ⚙️")
    log_info(
        f"✂️ Text Splitter: Processing {len(all_docs)} documents with 4000 chunk size and 200 overlap",
        Colors.YELLOW,
    )
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000,
                                                   chunk_overlap=200)
    splitted_docs = text_splitter.split_documents(all_docs)
    log_success(
        f"✂️ Text Splitter: Created {len(splitted_docs)} chunks from {len(all_docs)} documents",
    )

    # 5. Process documents asynchronously
    await index_documents_async(splitted_docs,
                                batch_size=500)

    log_header("🥳🥳🥳 PIPELINE COMPLETE 🥳🥳🥳")
    log_success("🎉 Documentation ingestion pipeline finished successfully!")
    log_info("📊 Summary:", Colors.BOLD)
    log_info(f"   • URLs mapped: {len(site_map['results'])}")
    log_info(f"   • Documents extracted: {len(all_docs)}")
    log_info(f"   • Chunks created: {len(splitted_docs)}")




if __name__ == '__main__':
    asyncio.run(main())