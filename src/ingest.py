import os
import shutil
import json
import logging
from langchain.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

from src.config import settings

logger = logging.getLogger("admissions_chatbot.ingest")
logging.basicConfig(level=logging.INFO)

def load_markdown_data(file_path: str) -> list[Document]:
    """Loads a markdown file and returns it as a list of LangChain Document objects."""
    logger.info(f"Loading markdown data from: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"Markdown file not found: {file_path}")
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Return as a single document; character splitter will divide it up
    return [Document(page_content=content, metadata={"source": file_path, "type": "markdown"})]

def load_faq_json_data(file_path: str) -> list[Document]:
    """Loads a JSON file containing FAQs and formats them as QA Document objects."""
    logger.info(f"Loading FAQ JSON data from: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"FAQ JSON file not found: {file_path}")
        return []
        
    with open(file_path, "r", encoding="utf-8") as f:
        faqs = json.load(f)
        
    documents = []
    for faq in faqs:
        question = faq.get("question", "")
        answer = faq.get("answer", "")
        text = f"Hỏi: {question}\nĐáp: {answer}"
        documents.append(Document(
            page_content=text, 
            metadata={"source": file_path, "type": "faq", "question": question}
        ))
        
    logger.info(f"Loaded {len(documents)} FAQ items.")
    return documents

def ingest_data():
    """Main ingestion pipeline."""
    # 1. Check for API key
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not set. Ingestion cannot proceed. Please add it to your .env file.")
        return

    # 2. Reset ChromaDB local database if it already exists
    if os.path.exists(settings.CHROMA_DB_DIR):
        logger.info(f"Cleaning existing database directory: {settings.CHROMA_DB_DIR}")
        try:
            shutil.rmtree(settings.CHROMA_DB_DIR)
        except Exception as e:
            logger.warning(f"Could not delete database directory: {e}. Chroma will merge or overwrite.")

    # 3. Load files
    docs = []
    docs.extend(load_markdown_data("data/majors_info.md"))
    docs.extend(load_faq_json_data("data/faq.json"))

    if not docs:
        logger.error("No documents loaded. Ingestion cancelled.")
        return

    # 4. Split text into chunks
    # For Vietnamese text, chunk_size around 800 chars and overlap 150 works well
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    split_docs = text_splitter.split_documents(docs)
    logger.info(f"Split documents into {len(split_docs)} chunks.")

    # 5. Initialize Google Embeddings
    # Use text-embedding-004 as recommended for Gemini embeddings
    logger.info("Initializing Google Generative AI Embeddings model...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=settings.GEMINI_API_KEY
    )

    # 6. Store in Chroma DB
    logger.info(f"Generating vectors and saving to ChromaDB at: {settings.CHROMA_DB_DIR}")
    try:
        vector_store = Chroma.from_documents(
            documents=split_docs,
            embedding=embeddings,
            persist_directory=settings.CHROMA_DB_DIR
        )
        # In langchain vectorstore Chroma, persist is done automatically in newer versions, 
        # but let's call it just in case it's an older langchain-community package.
        if hasattr(vector_store, "persist"):
            vector_store.persist()
            
        logger.info("Ingestion completed successfully! Local ChromaDB is ready.")
    except Exception as e:
        logger.error(f"Error during ingestion embedding process: {e}")

if __name__ == "__main__":
    ingest_data()
