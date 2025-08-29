C:\Users\user\Desktop\documentation_assistant_project\.venv\Scripts\python.exe C:\Users\user\Desktop\documentation_assistant_project\ingestion2.py 

============================================================
🚀  ⚙️ DOCUMENTATION INGESTION PIPELINE ⚙️
============================================================
📝  🗺️ TavilyMap: Starting to map documentation structure from https://python.langchain.com/
✅  ✅ TavilyMap: Successfully mapped 166 URLs from https://python.langchain.com/
📝  📦 URLs Processing: Split 166 URLs into 9 batches

============================================================
🚀  ⚙️ DOCUMENT EXTRACTION PHASE ⚙️
============================================================
📝  🔧 TavilyExtract: Starting concurrent extraction of 9 batches of URLs
📝  🔄 TavilyExtract: Processing batch 1 with 20 URLs
📝  🔄 TavilyExtract: Processing batch 2 with 20 URLs
📝  🔄 TavilyExtract: Processing batch 3 with 20 URLs
📝  🔄 TavilyExtract: Processing batch 4 with 20 URLs
📝  🔄 TavilyExtract: Processing batch 5 with 20 URLs
📝  🔄 TavilyExtract: Processing batch 6 with 20 URLs
📝  🔄 TavilyExtract: Processing batch 7 with 20 URLs
📝  🔄 TavilyExtract: Processing batch 8 with 20 URLs
📝  🔄 TavilyExtract: Processing batch 9 with 6 URLs
✅  ✅ TavilyExtract: Completed batch 9 - extracted 6 documents
✅  ✅ TavilyExtract: Completed batch 8 - extracted 20 documents
✅  ✅ TavilyExtract: Completed batch 2 - extracted 20 documents
✅  ✅ TavilyExtract: Completed batch 7 - extracted 20 documents
✅  ✅ TavilyExtract: Completed batch 5 - extracted 20 documents
✅  ✅ TavilyExtract: Completed batch 1 - extracted 20 documents
✅  ✅ TavilyExtract: Completed batch 3 - extracted 20 documents
✅  ✅ TavilyExtract: Completed batch 4 - extracted 20 documents
✅  ✅ TavilyExtract: Completed batch 6 - extracted 20 documents
✅  ✅ TavilyExtract: Extraction complete: Total pages extracted: 166

============================================================
🚀  ⚙️ DOCUMENTATION CHUNKING PHASE ⚙️
============================================================
📝  ✂️ Text Splitter: Processing 166 documents with 4000 chunk size and 200 overlap
✅  ✂️ Text Splitter: Created 1320 chunks from 166 documents

============================================================
🚀  ⚙️ VECTOR STORAGE PHASE ⚙️
============================================================
📝  📦 VectorStore Indexing: Preparing to add 1320 documents to vector store
📝  📦 VectorStore Indexing: Split into 3 batches of 500 documents each
Unclosed client session
client_session: <aiohttp.client.ClientSession object at 0x000002624C56AB40>
✅  VectorStore Indexing: Successfully added batch 3/3 (320 documents)
Unclosed client session
client_session: <aiohttp.client.ClientSession object at 0x000002624677A540>
Unclosed client session
client_session: <aiohttp.client.ClientSession object at 0x00000262451208F0>
✅  VectorStore Indexing: Successfully added batch 2/3 (500 documents)
✅  VectorStore Indexing: Successfully added batch 1/3 (500 documents)
✅  VectorStore Indexing: All batches processed successfully! (3/3)

============================================================
🚀  🥳🥳🥳 PIPELINE COMPLETE 🥳🥳🥳
============================================================
✅  🎉 Documentation ingestion pipeline finished successfully!
📝  📊 Summary:
📝     • URLs mapped: 166
📝     • Documents extracted: 166
📝     • Chunks created: 1320

Process finished with exit code 0