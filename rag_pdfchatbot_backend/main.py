import os
import shutil 
import uuid
import json
import threading
import hashlib
import datetime
import tempfile
import logging
import asyncio 
from io import BytesIO
from typing import Dict, Any, List, Optional, Union
import subprocess
import uvicorn
import time
import requests
from dotenv import load_dotenv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# FastAPI and related imports
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Query, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl 
from werkzeug.utils import secure_filename
from contextlib import asynccontextmanager  

# LangChain imports
from transformers import AutoTokenizer
from langchain_core.embeddings import Embeddings
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader 
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain.schema import AIMessage, HumanMessage, BaseMessage
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter
from bs4 import BeautifulSoup
import onnxruntime as ort

# --- FAISS Parallel Search Support ---
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# --- Configure logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Load environment variables ---
load_dotenv()
os.environ["USER_AGENT"] = "RAG Chatbot Assistant/1.0"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    logger.error("OPENROUTER_API_KEY is not set in environment.")
    raise ValueError("OPENROUTER_API_KEY is not set in environment.")

# --- Constants and Configurations ---
class Config:
    # Updated FAISS_DB_DIR to be the parent directory for all sessions
    FAISS_DB_DIR = "user_data"  
    UPLOAD_DIR = "temp_uploads" 
    MAX_UPLOAD_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    LLM_MODEL = "deepseek/deepseek-chat-v3-0324:free"
    DEFAULT_TEMPERATURE = 0.5
    MIN_TEMPERATURE = 0.0
    MAX_TEMPERATURE = 1.5
    RETRIEVER_K = 4 
    MAX_WEB_SCRAPE_CONTENT_LENGTH = 200000 
    MAX_SUMMARY_INPUT_LENGTH = 10000 
    SESSION_EXPIRATION_MINUTES = 60  # 1 hour
    RETRIEVER_FETCH_K = 20    # Number of docs to fetch before MMR filtering
    MMR_LAMBDA = 0.3          # Balance relevance/diversity: 1.0 = pure similarity, 0 = max diversity
    # Performance optimization
    CACHE_SIZE = 1000  # Number of items to cache
    MAX_RETRIEVAL_TIME = 10.0  # Maximum time for retrieval in seconds
    MAX_CONTEXT_CHARS = 4000  # Limit RAG context passed to LLM

# --- Ensure directories exist ---
os.makedirs(Config.FAISS_DB_DIR, exist_ok=True) # Ensure FAISS DB directory exists
os.makedirs(Config.UPLOAD_DIR, exist_ok=True) # Ensure this exists if temp files were to use it
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# --- Set FAISS parallel search threads (if available) ---
FAISS_NUM_THREADS = max(1, (os.cpu_count() or 1))  # Dynamically set based on available CPU cores
if FAISS_AVAILABLE:
    try:
        faiss.omp_set_num_threads(FAISS_NUM_THREADS)
        print(f"\033[92m✓ FAISS parallel search: omp_set_num_threads({FAISS_NUM_THREADS}) (detected CPUs)\033[0m")
    except Exception as e:
        print(f"\033[93m! Warning: Could not set FAISS parallel threads: {e}\033[0m")


# --- ONNX MiniLM Embedder ---
class ONNXMiniLMEmbedder(Embeddings):
    def __init__(self, model_dir: str, quantized: bool = False):
        """Initialize the ONNX embedder."""
        super().__init__()
        self.model_dir = model_dir
        self.quantized = quantized
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self._initialize_model()

    def _initialize_model(self):
        """Initialize or reinitialize the model based on quantization setting."""
        model_path = os.path.join(
            self.model_dir, 
            "model-quantized.onnx" if self.quantized else "model.onnx"
        )
        
        if not os.path.exists(model_path):
            error_msg = f"ONNX model not found at {model_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Close existing session if it exists
        if hasattr(self, 'session'):
            del self.session
            
        self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.input_names = {inp.name for inp in self.session.get_inputs()}
        self.output_name = self.session.get_outputs()[0].name
        self.embedding_dim = self._get_embedding_dimension()

    def set_quantized(self, quantized: bool):
        """Switch between quantized and regular model."""
        if quantized != self.quantized:
            self.quantized = quantized
            self._initialize_model()
            logger.info(f"Switched to {'quantized' if quantized else 'regular'} model")

    def _get_embedding_dimension(self) -> int:
        """Determine the embedding dimension by running a test inference"""
        try:
            test_text = "test"
            inputs = self.tokenizer(
                test_text,
                max_length=128,
                padding='max_length',
                truncation=True,
                return_tensors='np'
            )
            
            input_ids = inputs["input_ids"].astype(np.int64)
            attention_mask = inputs["attention_mask"].astype(np.int64)
            
            ort_inputs = {
                "input_ids": input_ids,
                "attention_mask": attention_mask
            }
            
            if "token_type_ids" in self.input_names:
                token_type_ids = np.zeros_like(input_ids, dtype=np.int64)
                ort_inputs["token_type_ids"] = token_type_ids
                
            outputs = self.session.run([self.output_name], ort_inputs)
            output_shape = outputs[0].shape
            return output_shape[-1]  # Return the last dimension size
        except Exception as e:
            logger.warning(f"Could not determine embedding dimension: {e}")
            return 384  # Default for MiniLM

    def __call__(self, text: str) -> List[float]:
        """Make the instance callable for compatibility with LangChain."""
        return self.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        return [self._embed_text(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        return self._embed_text(text)

    def _embed_text(self, text: str) -> List[float]:
        """Tokenize and run ONNX model inference to get embedding."""
        inputs = self.tokenizer(
            text,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_tensors='np'
        )
        
        input_ids = inputs["input_ids"].astype(np.int64)
        attention_mask = inputs["attention_mask"].astype(np.int64)
        
        ort_inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        }
        
        if "token_type_ids" in self.input_names:
            token_type_ids = np.zeros_like(input_ids, dtype=np.int64)
            ort_inputs["token_type_ids"] = token_type_ids
        
        outputs = self.session.run([self.output_name], ort_inputs)
        embedding = outputs[0][0].flatten()
        
        # Normalize embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.tolist()


# --- Thread safety ---
vectorstore_lock = threading.Lock() # For protecting vectorstore initialization and writes/deletes

# --- Embeddings and Vectorstore Initialization ---
onnx_model_dir = "onnx_model"
if not os.path.exists(onnx_model_dir):
    error_msg = f"ONNX model directory not found at {onnx_model_dir}. Please download the model and place it in this directory."
    logger.error(error_msg)
    raise FileNotFoundError(error_msg)

embeddings = ONNXMiniLMEmbedder(model_dir=onnx_model_dir)

def update_last_activity(session_id: str):
    """Updates the last activity timestamp for a session."""
    session_dir = os.path.join(Config.FAISS_DB_DIR, session_id)
    metadata_path = os.path.join(session_dir, "metadata.json")
    try:
        # Create session directory if it doesn't exist
        os.makedirs(session_dir, exist_ok=True)
        # Load existing metadata if it exists
        metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        # Update last activity timestamp
        metadata["last_activity"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        # Save updated metadata
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)
    except Exception as e:
        logger.error(f"Error updating last activity for session {session_id}: {e}")

def get_session_dir(session_id: str) -> str:
    """Get the directory for a specific session."""
    session_dir = os.path.join(Config.FAISS_DB_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    return session_dir

def get_or_init_vectorstore(session_id: str) -> FAISS:
    """Get or initialize a session-specific vectorstore."""
    session_dir = get_session_dir(session_id)
    # Update last activity
    update_last_activity(session_id)
    # Check if vectorstore already exists for this session
    index_path = os.path.join(session_dir, "index.faiss")
    if os.path.exists(index_path):
        try:
            # DEBUG: Session loading
            print(f"\033[92m✓ Session {session_id} vectorstore found at {index_path}\033[0m")
            return FAISS.load_local(
                session_dir, 
                embeddings,
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            logger.warning(f"Failed to load existing index for session {session_id}: {e}. Creating new one.")
            print(f"\033[93m! Warning: Could not load existing vectorstore for session {session_id}, creating new one\033[0m")
    # Create new vectorstore
    print(f"\033[96m→ Creating new vectorstore for session {session_id}\033[0m")
    vectorstore = FAISS.from_texts(
        ["Initial dummy document"],
        embeddings
    )
    vectorstore.delete([vectorstore.index_to_docstore_id[0]])
    vectorstore.save_local(session_dir)
    return vectorstore

def get_session_temperature(session_id: str) -> float:
    """Get the temperature setting for a specific session."""
    session_dir = get_session_dir(session_id)
    settings_path = os.path.join(session_dir, "settings.json")
    try:
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings = json.load(f)
                return settings.get("temperature", Config.DEFAULT_TEMPERATURE)
        else:
            # Create default settings
            default_settings = {"temperature": Config.DEFAULT_TEMPERATURE}
            with open(settings_path, "w") as f:
                json.dump(default_settings, f)
            return Config.DEFAULT_TEMPERATURE
    except Exception as e:
        logger.error(f"Error loading session temperature for {session_id}: {e}")
        return Config.DEFAULT_TEMPERATURE

def set_session_temperature(session_id: str, temperature: float) -> float:
    """Set the temperature setting for a specific session."""
    # Clamp temperature to valid range
    temp = max(Config.MIN_TEMPERATURE, min(Config.MAX_TEMPERATURE, temperature))
    session_dir = get_session_dir(session_id)
    settings_path = os.path.join(session_dir, "settings.json")
    try:
        # Load existing settings or create new ones
        settings = {}
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings = json.load(f)
        # Update temperature
        settings["temperature"] = temp
        # Save settings
        with open(settings_path, "w") as f:
            json.dump(settings, f)
        print(f"\033[92m✓ Temperature set to {temp:.2f} for session {session_id}\033[0m")
        return temp
    except Exception as e:
        logger.error(f"Error saving session temperature for {session_id}: {e}")
        return Config.DEFAULT_TEMPERATURE

def cleanup_expired_sessions():
    """Clean up expired sessions."""
    now = datetime.datetime.now(datetime.timezone.utc)
    expiration_time = now - datetime.timedelta(minutes=Config.SESSION_EXPIRATION_MINUTES)
    if not os.path.exists(Config.FAISS_DB_DIR):
        return
    print(f"\033[95m{'='*50}")
    print(f"SESSION CLEANUP CHECK: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Expiring sessions inactive since: {expiration_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\033[0m")
    for session_id in os.listdir(Config.FAISS_DB_DIR):
        session_path = os.path.join(Config.FAISS_DB_DIR, session_id)
        if not os.path.isdir(session_path):
            continue
        metadata_path = os.path.join(session_path, "metadata.json")
        if not os.path.exists(metadata_path):
            # If no metadata, assume it's expired
            print(f"\033[91m× Session {session_id} has no metadata - marking for deletion\033[0m")
            try:
                shutil.rmtree(session_path)
                logger.info(f"Deleted session {session_id} with no metadata")
                print(f"\033[91m× Deleted session {session_id} (no metadata)\033[0m")
            except Exception as e:
                logger.error(f"Error deleting session {session_id}: {e}")
            continue
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            last_activity = datetime.datetime.fromisoformat(metadata["last_activity"])
            if last_activity < expiration_time:
                try:
                    print(f"\033[91m× Session {session_id} expired (last active: {last_activity.strftime('%Y-%m-%d %H:%M:%S')})\033[0m")
                    shutil.rmtree(session_path)
                    logger.info(f"Deleted expired session {session_id}")
                    print(f"\033[91m× Deleted expired session {session_id}\033[0m")
                except Exception as e:
                    logger.error(f"Error deleting session {session_id}: {e}")
            else:
                print(f"\033[92m✓ Session {session_id} active (last active: {last_activity.strftime('%Y-%m-%d %H:%M:%S')})\033[0m")
        except Exception as e:
            logger.error(f"Error checking session {session_id}: {e}")
            # If there's an error, try to delete the session to be safe
            try:
                print(f"\033[91m× Session {session_id} had metadata error - marking for deletion\033[0m")
                shutil.rmtree(session_path)
                logger.info(f"Deleted session {session_id} due to error")
                print(f"\033[91m× Deleted session {session_id} (metadata error)\033[0m")
            except Exception as e:
                logger.error(f"Error deleting problematic session {session_id}: {e}")

# --- LLM Setup ---
def create_llm(temperature: float = Config.DEFAULT_TEMPERATURE):
    """Create an LLM instance with the specified temperature."""
    # Clamp temperature to valid range
    temp = max(Config.MIN_TEMPERATURE, min(Config.MAX_TEMPERATURE, temperature))
    return ChatOpenAI(
        model=Config.LLM_MODEL,
        openai_api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=temp,
        timeout=30.0,  # Add timeout for reliability
        max_retries=3,  # Add retries for network issues
    )

# --- Tools ---
@tool
def current_datetime_tool() -> str:
    """Returns the current date and time in YYYY-MM-DD HH:MM:SS format."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def search_web_tool(query: str) -> str:
    """Search the web for information about a query."""
    try:
        # This is a placeholder - in a real implementation, you'd use a search API
        return f"Web search results for '{query}' would be shown here."
    except Exception as e:
        return f"Error performing web search: {str(e)}"

tools = [current_datetime_tool]  # Only current_datetime_tool remains as a direct agent tool

# --- Agent Setup ---
def create_agent_executor(temperature: float = Config.DEFAULT_TEMPERATURE):
    """Create an agent executor with the specified temperature."""
    llm = create_llm(temperature)
    agent_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """
            You are an AI assistant specialized in:
            - Logistics
            - Postal services
            - Research papers
            - Web content
            You have access to the following tools: {tools}
            ### Instructions:
            - Use `current_datetime_tool` for questions about the current date or time
            - If you don’t know the answer and no tool helps, say so clearly
            - Be concise and professional
            - Be more creative when temperature is high; more factual when low
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    ).partial(tools=", ".join([tool.name for tool in tools]))
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=agent_prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# --- Utilities ---
def hash_content(content: Union[bytes, str]) -> str:
    """Generates a SHA256 hash for the given bytes or string."""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()

def load_ingested_hashes(session_id: str) -> List[str]:
    """Loads the list of ingested file/URL hashes for a specific session."""
    session_dir = get_session_dir(session_id)
    hashes_file = os.path.join(session_dir, "ingested_hashes.json")
    try:
        if not os.path.exists(hashes_file):
            logger.info(f"Hashes file not found at {hashes_file}. Creating empty file.")
            with open(hashes_file, "w") as f:
                json.dump([], f)
            print(f"\033[96m→ Created new hashes file for session {session_id}\033[0m")
            return []
        with open(hashes_file, "r") as f:
            hashes = json.load(f)
            print(f"\033[92m✓ Loaded {len(hashes)} hashes for session {session_id}\033[0m")
            return hashes
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {hashes_file}. File might be corrupted. Initializing with empty list.")
        print(f"\033[93m! Warning: Hashes file corrupted for session {session_id}, resetting\033[0m")
        return []
    except Exception as e:
        logger.error(f"Error loading ingested hashes: {e}")
        print(f"\033[91m× Error loading hashes for session {session_id}: {str(e)[:50]}...\033[0m")
        return []

def save_ingested_hashes(session_id: str, hashes: List[str]):
    """Saves the list of ingested file/URL hashes for a specific session."""
    session_dir = get_session_dir(session_id)
    hashes_file = os.path.join(session_dir, "ingested_hashes.json")
    try:
        with open(hashes_file, "w") as f:
            json.dump(hashes, f)
        print(f"\033[92m✓ Saved {len(hashes)} hashes for session {session_id}\033[0m")
    except Exception as e:
        logger.error(f"Error saving ingested hashes: {e}")
        print(f"\033[91m× Error saving hashes for session {session_id}: {str(e)[:50]}...\033[0m")

def is_duplicate(session_id: str, hash_value: str) -> bool:
    """Checks if a content hash already exists in the ingested list for a session."""
    hashes = load_ingested_hashes(session_id)
    is_dup = hash_value in hashes
    if is_dup:
        print(f"\033[93m! Duplicate detected for session {session_id}: {hash_value[:8]}...\033[0m")
    else:
        print(f"\033[92m✓ New content for session {session_id}: {hash_value[:8]}...\033[0m")
    return is_dup

def add_hash(session_id: str, hash_value: str):
    """Adds a new hash to the ingested list and saves it for a session."""
    hashes = load_ingested_hashes(session_id)
    if hash_value not in hashes:
        hashes.append(hash_value)
        save_ingested_hashes(session_id, hashes)
        print(f"\033[92m✓ Added hash to session {session_id}: {hash_value[:8]}...\033[0m")
    else:
        print(f"\033[93m! Hash already exists in session {session_id}: {hash_value[:8]}...\033[0m")

async def process_and_ingest_documents_background(session_id: str, documents: List[Any], source_name: str, source_type: str, url: Optional[str] = None):
    """
    Processes documents, chunks them, and ingests them into the vectorstore.
    Runs in a background task.
    """
    print(f"\033[96m{'='*70}")
    print(f"PROCESSING {source_type.upper()}: '{source_name}' for session {session_id}")
    print(f"{'='*70}\033[0m")
    try:
        # Add metadata for chunking
        print(f"\033[96m→ Processing {len(documents)} documents...\033[0m")
        for i, doc in enumerate(documents):
            doc.metadata["source"] = source_name
            if source_type == "pdf":
                doc.metadata["page"] = i + 1  # Page number for PDFs
                print(f"\033[96m  Document {i+1}: Page {i+1}\033[0m")
            elif source_type == "web":
                doc.metadata["url"] = url if url else source_name  # Ensure URL is stored explicitly
                print(f"\033[96m  Document {i+1}: URL fragment\033[0m")
            doc.metadata["file_uuid"] = str(uuid.uuid4())  # Unique ID for each document chunk
        # Use a more sophisticated text splitter for better quality
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=[
                "\n\n\n",  # Triple newlines (section breaks)
                "\n\n",    # Double newlines (paragraph breaks)
                "\n",      # Single newline (line breaks)
                " ",       # Spaces (word boundaries)
                ".",       # Periods (sentence endings)
                "",        # Empty string (character level)
            ],
            keep_separator=True,
            is_separator_regex=False,
        )
        chunks = splitter.split_documents(documents)
        print(f"\033[92m✓ Split into {len(chunks)} chunks\033[0m")
        # Get session-specific vectorstore
        store = get_or_init_vectorstore(session_id)
        with vectorstore_lock:  # Protect write operations to Faiss
            store.add_documents(chunks)
            store.save_local(get_session_dir(session_id))  # Save changes to disk
            print(f"\033[92m✓ Added {len(chunks)} chunks to vectorstore for session {session_id}\033[0m")
        print(f"\033[92m✓ Processed and ingested {len(chunks)} chunks for {source_name} ({source_type}) in session {session_id}.\033[0m")
        # Update last activity
        update_last_activity(session_id)
    except Exception as e:
        logger.error(f"Failed to process and ingest {source_type} '{source_name}' for session {session_id}: {e}", exc_info=True)
        print(f"\033[91m× Error processing {source_type} '{source_name}' for session {session_id}: {str(e)[:100]}...\033[0m")

def clean_web_content(html_content: str) -> str:
    """Extracts and cleans text from HTML content using BeautifulSoup."""
    try:
        print(f"\033[96m→ Cleaning web content ({len(html_content)} characters)...\033[0m")
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove common non-content elements
        for element in soup(["nav", "header", "footer", "aside", "script", "style", "meta", "link"]):
            element.extract()
        
        # Remove ads and trackers
        for element in soup.find_all(class_=lambda x: x and any(keyword in x.lower() for keyword in ['ad', 'banner', 'sidebar', 'widget'])):
            element.extract()
        
        # Extract text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        print(f"\033[92m✓ Cleaned web content ({len(text)} characters)\033[0m")
        return text[:Config.MAX_WEB_SCRAPE_CONTENT_LENGTH]
    except Exception as e:
        logger.error(f"Error cleaning web content: {str(e)}", exc_info=True)
        print(f"\033[91m× Error cleaning web content: {str(e)[:100]}...\033[0m")
        # Return a limited portion of the original content as fallback
        return html_content[:Config.MAX_WEB_SCRAPE_CONTENT_LENGTH]

# --- Lifespan Management (replaces deprecated on_event) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup: Start the cleanup task
    print(f"\033[95m{'='*50}")
    print(f"STARTING RAG CHATBOT API - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\033[0m")
    print(f"\033[92m✓ Embedding model: {Config.EMBEDDING_MODEL}\033[0m")
    print(f"\033[92m✓ LLM model: {Config.LLM_MODEL}\033[0m")
    print(f"\033[92m✓ Session expiration: {Config.SESSION_EXPIRATION_MINUTES} minutes\033[0m")
    print(f"\033[92m✓ User data directory: {os.path.abspath(Config.FAISS_DB_DIR)}\033[0m")
    logger.info("Starting session cleanup task...")
    cleanup_task = None
    async def cleanup_loop():
        while True:
            cleanup_expired_sessions()
            await asyncio.sleep(15 * 60)  # Sleep 15 minutes
    try:
        cleanup_task = asyncio.create_task(cleanup_loop())
        print(f"\033[92m✓ Session cleanup task started\033[0m")
        logger.info("Session cleanup task started")
        yield  # Application runs here
    finally:
        # Shutdown: Cancel the cleanup task
        if cleanup_task:
            print(f"\033[95m{'='*50}")
            print(f"SHUTTING DOWN RAG CHATBOT API - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*50}\033[0m")
            print(f"\033[93m→ Stopping session cleanup task...\033[0m")
            cleanup_task.cancel()
            await asyncio.wait([cleanup_task], timeout=5.0)
            print(f"\033[92m✓ Session cleanup task stopped\033[0m")
            logger.info("Session cleanup task stopped")

# --- FastAPI App (with lifespan) ---
app = FastAPI(
    title="RAG Chatbot API",
    description="Chatbot leveraging RAG and custom tools for logistics, postal services, research papers, and web content.",
    version="2.0.0",
    lifespan=lifespan  # Use the lifespan context manager
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Request/Response ---
class SourceMetadata(BaseModel):
    source: str = Field(..., description="The filename or URL of the source document.")
    page: Union[int, str] = Field(..., description="The page number from the source document (or URL for web).")

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's query or message.")
    chat_history: List[Dict[str, str]] = Field([], description="Previous conversation history.")
    temperature: Optional[float] = Field(
        None, 
        ge=Config.MIN_TEMPERATURE, 
        le=Config.MAX_TEMPERATURE,
        description="Temperature parameter for the LLM (0.0 = deterministic, 1.5 = creative). If not provided, uses session default."
    )

class ChatResponse(BaseModel):
    response: str = Field(..., description="The AI's generated response.")
    source_type: str = Field(..., description="Indicates if the response is from 'RAG', 'Tool', or 'LLM_Internal_Knowledge'.")
    retrieved_sources: List[SourceMetadata] = Field([], description="List of source documents/URLs used for RAG responses.")
    tool_used: Optional[str] = Field(None, description="Name of the tool used, if any.")
    temperature: float = Field(..., description="The temperature setting used for this response.")

class IngestResponse(BaseModel): 
    message: str = Field(..., description="Status message for the ingestion.")
    source_name: Optional[str] = Field(None, description="Name of the ingested source (filename or URL).")
    content_hash: Optional[str] = Field(None, description="SHA256 hash of the ingested content.")
    source_type: str = Field(..., description="Type of source ingested: 'pdf' or 'web'.")

class DeleteResponse(BaseModel):
    message: str = Field(..., description="Status message for vector removal.")

class SummarizeResponse(BaseModel):
    summary: str = Field(..., description="The summarized content.")

class SettingsResponse(BaseModel):
    temperature: float = Field(..., description="Current temperature setting for this session.")
    chunk_size: int = Field(..., description="Current chunk size for document processing.")
    retriever_k: int = Field(..., description="Number of documents retrieved for RAG.")

# --- API Endpoints ---
@app.get("/health", summary="Health Check")
async def health_check():
    """Checks the health of the API."""
    print(f"\033[92m✓ Health check requested\033[0m")
    print(f"\033[92m✓ API is healthy - {datetime.datetime.now().isoformat()}\033[0m")
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

# ── Helper functions for true MMR scoring ──────────────────────────────

def compute_mmr_scores(query_emb: np.ndarray, doc_embs: np.ndarray, lambda_mult: float, k: int):
    """
    Compute true MMR scores for the top-k selection.
    Returns a tuple (selected_indices, mmr_scores).
    """
    selected, scores = [], []
    query_sim = cosine_similarity([query_emb], doc_embs)[0]
    remaining = list(range(len(doc_embs)))

    for _ in range(min(k, len(doc_embs))):
        best_idx, best_score = None, -float("inf")
        for i in remaining:
            rel = query_sim[i]
            div = (
                0
                if not selected
                else max(
                    cosine_similarity([doc_embs[i]], [doc_embs[j]])[0][0]
                    for j in selected
                )
            )
            mmr = lambda_mult * rel - (1 - lambda_mult) * div
            if mmr > best_score:
                best_idx, best_score = i, mmr

        selected.append(best_idx)
        scores.append(best_score)
        remaining.remove(best_idx)

    return selected, scores


def custom_mmr_retrieve(vectorstore, query: str, k: int, fetch_k: int, lambda_mult: float):
    """
    Fetch fetch_k by raw similarity, then re-rank top-k by true MMR.
    Returns List[(Document, mmr_score)].
    """
    # 1) fetch top-`fetch_k` by raw similarity
    docs_and_sim = vectorstore.similarity_search_with_score(query, k=fetch_k)

    if not docs_and_sim:
        print("⚠️ No documents retrieved during similarity search.")
        return []

    docs, _ = zip(*docs_and_sim)

    # 2) embed query + docs
    query_emb = vectorstore.embedding_function.embed_query(query)
    doc_texts = [doc.page_content for doc in docs]
    doc_embs = np.array(vectorstore.embedding_function.embed_documents(doc_texts))

    # 3) compute MMR
    selected_idxs, mmr_scores = compute_mmr_scores(query_emb, doc_embs, lambda_mult, k)

    # 4) return selected docs with their MMR scores
    return [(docs[i], mmr_scores[idx]) for idx, i in enumerate(selected_idxs)]


# ── Your Chat Endpoint ─────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse, summary="Chat with the RAG Bot")
async def chat_endpoint(
    request: ChatRequest,
    session_id: str = Query(...),
):
    # Update last activity and temperature
    update_last_activity(session_id)
    session_temp = get_session_temperature(session_id)
    temperature = (
        request.temperature
        if request.temperature is not None
        else session_temp
    )
    temperature = max(Config.MIN_TEMPERATURE, min(Config.MAX_TEMPERATURE, temperature))

    # Logging header
    print(f"\n\033[95m{'='*70}")
    print(f"NEW CHAT REQUEST - Session: {session_id}")
    print(f"{'='*70}\033[0m")
    print(f"\033[96m→ User query: '{request.query}'\033[0m")
    print(f"\033[96m→ Temperature: {temperature:.2f}\033[0m")

    response_source_type = "LLM_Internal_Knowledge"
    used_tool = None
    retrieved_docs_metadata: List[SourceMetadata] = []
    response_content = "I could not generate a response."

    # Reconstruct history messages
    messages: List[BaseMessage] = []
    for msg in request.chat_history:
        if msg.get("role") == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg.get("role") == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    try:
        # 1) Init vectorstore
        vectorstore = get_or_init_vectorstore(session_id)

        # 2) Custom MMR retrieval
        print(f"\033[96m→ Performing MMR retrieval (k={Config.RETRIEVER_K}, fetch_k={Config.RETRIEVER_FETCH_K})...\033[0m")
        try:
            raw_results = custom_mmr_retrieve(
                vectorstore=vectorstore,
                query=request.query,
                k=Config.RETRIEVER_K,
                fetch_k=Config.RETRIEVER_FETCH_K,
                lambda_mult=Config.MMR_LAMBDA,
            )
            if not raw_results:
                docs, scores = [], []
            else:
                docs, scores = zip(*raw_results)
        except Exception as mmr_err:
            print(f"❌ Error during custom MMR retrieval: {mmr_err}")
            docs, scores = [], []

        if docs:
            response_source_type = "RAG"
            print(f"\033[92m✓ Retrieved {len(docs)} docs via MMR\033[0m")

            # Debug print each chunk and score
            for i, (doc, score) in enumerate(raw_results, start=1):
                src = doc.metadata.get("source", "unknown")
                loc = doc.metadata.get("page", doc.metadata.get("url", "N/A"))
                print(f"\n\033[94m--- Chunk {i} ---\033[0m")
                print(f"Source: {src}, Location: {loc}")
                print(f"MMR Score: {score:.4f}")
                preview = doc.page_content[:200].replace('\n', ' ')
                print(f"Content preview: {preview}{'...' if len(doc.page_content) > 200 else ''}")

                # Build context
                retrieved_docs_metadata.append(SourceMetadata(source=src, page=loc))

            # Assemble context for RAG
            context = "\n\n".join(
                f"Source: {meta.source}, Location: {meta.page}\nContent: {docs[i].page_content}"
                for i, meta in enumerate(retrieved_docs_metadata)
            )

            # Create and invoke RAG chain (unchanged)
            rag_prompt = ChatPromptTemplate.from_messages([
                ("system", """
                You are an AI assistant. Answers must be based solely on the retrieved context.
                """),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            llm = create_llm(temperature)
            rag_chain = (
                RunnablePassthrough.assign(
                    context=lambda x: context,
                    chat_history=lambda x: x["chat_history"],
                    input=lambda x: x["input"],
                )
                | rag_prompt
                | llm
                | RunnableLambda(lambda x: x.content)
            )
            response_content = await rag_chain.ainvoke({
                "input": request.query,
                "chat_history": messages,
            })

        else:
            # Fallback to Agent/Tool
            print(f"\033[93m! No docs found, falling back\033[0m")
            agent_executor = create_agent_executor(temperature)
            agent_result = await agent_executor.ainvoke({
                "input": request.query,
                "chat_history": messages,
            })
            response_content = agent_result.get("output", response_content)
            # detect tool usage...
        
        # Final logging & return
        print(f"\n\033[95m{'='*70}")
        print(f"Source Type: {response_source_type}")
        print(f"Retrieved Sources: {len(retrieved_docs_metadata)}")
        print(f"{'='*70}\033[0m")

        return ChatResponse(
            response=response_content,
            source_type=response_source_type,
            retrieved_sources=retrieved_docs_metadata,
            tool_used=used_tool,
            temperature=temperature,
        )

    except Exception as e:
        logger.error("Error in chat endpoint", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing request")






@app.post("/ingest", response_model=IngestResponse, summary="Ingest a PDF Document or Web Page Link")
async def ingest_endpoint(
    background_tasks: BackgroundTasks,
    session_id: str = Query(...),  # Add session_id parameter
    file: Optional[UploadFile] = File(None, description="The PDF file to upload."),
    url: Optional[HttpUrl] = Form(None, description="The URL of the web page to ingest.")
):
    """
    Ingests a PDF file or a web page link, checks for duplicates, and initiates its processing
    and ingestion into the vector store in the background.
    Only one of `file` or `url` should be provided.
    """
    # Update last activity
    update_last_activity(session_id)
    print(f"\033[95m{'='*70}")
    print(f"INGEST REQUEST - Session: {session_id}")
    print(f"{'='*70}\033[0m")
    if not file and not url:
        print(f"\033[91m× Error: Either a PDF file or a web page URL must be provided.\033[0m")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either a PDF file or a web page URL must be provided.")
    if file and url:
        print(f"\033[91m× Error: Cannot provide both a PDF file and a URL. Please provide only one.\033[0m")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot provide both a PDF file and a URL. Please provide only one.")
    if file:
        if not file.filename:
            print(f"\033[91m× Error: No file name provided.\033[0m")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file name provided.")
        if not file.filename.lower().endswith(".pdf"):
            print(f"\033[91m× Error: Only PDF files are allowed for file uploads.\033[0m")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed for file uploads.")
        print(f"\033[96m→ Processing PDF file: {file.filename}\033[0m")

        # Check file size incrementally to avoid loading large files into memory
        content = b""
        chunk_size = 1024 * 256  # 256KB chunks
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            content += chunk
            if len(content) > Config.MAX_UPLOAD_FILE_SIZE:
                print(f"\033[91m× Error: File too large. Maximum size is {Config.MAX_UPLOAD_FILE_SIZE / (1024 * 1024):.0f} MB.\033[0m")
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Maximum size is {Config.MAX_UPLOAD_FILE_SIZE / (1024 * 1024):.0f} MB."
                )
        content_hash = hash_content(content)
        safe_filename = secure_filename(file.filename)
        print(f"\033[96m→ File size: {len(content) / (1024 * 1024):.2f} MB\033[0m")
        print(f"\033[96m→ Content hash: {content_hash[:16]}...\033[0m")
        if is_duplicate(session_id, content_hash):
            print(f"\033[93m! Duplicate upload detected for '{safe_filename}' (hash: {content_hash[:8]}...)\033[0m")
            logger.info(f"Duplicate upload detected for '{safe_filename}' (hash: {content_hash}) in session {session_id}.")
            return IngestResponse(message=f"'{safe_filename}' has already been uploaded and ingested.", source_name=safe_filename, content_hash=content_hash, source_type="pdf")
        print(f"\033[92m✓ New file detected: {safe_filename}\033[0m")
        add_hash(session_id, content_hash) 

        # Process PDF
        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            print(f"\033[96m→ Temporary file created: {tmp_file_path}\033[0m")
            loader = PyPDFLoader(tmp_file_path)
            print(f"\033[96m→ Loading PDF document...\033[0m")
            pages = loader.load()
            print(f"\033[92m✓ Loaded {len(pages)} pages from PDF\033[0m")
            background_tasks.add_task(process_and_ingest_documents_background, session_id, pages, safe_filename, "pdf")
            print(f"\033[92m✓ Added background task for PDF processing\033[0m")
        except Exception as e:
            print(f"\033[91m× Error handling PDF upload for '{safe_filename}' in session {session_id}: {str(e)[:100]}...\033[0m")
            logger.error(f"Error handling PDF upload for '{safe_filename}' in session {session_id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process PDF file.")
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                print(f"\033[93m→ Cleaned up temporary file: {tmp_file_path}\033[0m")
                logger.info(f"Cleaned up temporary file: {tmp_file_path}")
        print(f"\033[92m✓ File '{safe_filename}' (hash: {content_hash[:8]}...) received and scheduled for processing in session {session_id}.\033[0m")
        logger.info(f"File '{safe_filename}' (hash: {content_hash}) received and scheduled for processing in session {session_id}.")
        return IngestResponse(message=f"File '{safe_filename}' is being processed in the background.", source_name=safe_filename, content_hash=content_hash, source_type="pdf")
    elif url:
        url_str = str(url)
        content_hash = hash_content(url_str)  # Hash the URL itself for duplicate checking
        print(f"\033[96m→ Processing URL: {url_str}\033[0m")
        print(f"\033[96m→ URL hash: {content_hash[:16]}...\033[0m")
        if is_duplicate(session_id, content_hash):
            print(f"\033[93m! Duplicate ingestion detected for URL '{url_str}' (hash: {content_hash[:8]}...)\033[0m")
            logger.info(f"Duplicate ingestion detected for URL '{url_str}' (hash: {content_hash}) in session {session_id}.")
            return IngestResponse(message=f"URL '{url_str}' has already been ingested.", source_name=url_str, content_hash=content_hash, source_type="web")
        print(f"\033[92m✓ New URL detected: {url_str}\033[0m")
        add_hash(session_id, content_hash)
        try:

            # Using WebBaseLoader directly for web content
            print(f"\033[96m→ Scheduling URL ingestion task...\033[0m")
            background_tasks.add_task(ingest_web_page_background, session_id, url_str)
            print(f"\033[92m✓ Added background task for URL processing\033[0m")
            print(f"\033[92m✓ URL '{url_str}' (hash: {content_hash[:8]}...) received and scheduled for processing in session {session_id}.\033[0m")
            logger.info(f"URL '{url_str}' (hash: {content_hash}) received and scheduled for processing in session {session_id}.")
            return IngestResponse(message=f"URL '{url_str}' is being processed in the background.", source_name=url_str, content_hash=content_hash, source_type="web")
        except Exception as e:
            print(f"\033[91m× Error handling URL ingestion for '{url_str}' in session {session_id}: {str(e)[:100]}...\033[0m")
            logger.error(f"Error handling URL ingestion for '{url_str}' in session {session_id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process web page URL.")

async def ingest_web_page_background(session_id: str, url: str):
    """Fetches, cleans, and ingests a web page in a background task."""
    print(f"\033[95m{'='*70}")
    print(f"PROCESSING URL - Session: {session_id}")
    print(f"URL: {url}")
    print(f"{'='*70}\033[0m")
    try:
        print(f"\033[96m→ Loading web content from {url}...\033[0m")
        loader = WebBaseLoader(url)
        documents = loader.load()
        if not documents:
            print(f"\033[91m× No content loaded from URL: {url}\033[0m")
            logger.warning(f"No content loaded from URL: {url}")
            return
        print(f"\033[92m✓ Loaded {len(documents)} document fragments from {url}\033[0m")

        # Ensure content is cleaned before processing
        for doc in documents:
            doc.page_content = clean_web_content(doc.page_content)

            # Ensure the correct metadata for source and url
            doc.metadata["source"] = url
            doc.metadata["url"] = url 
        await process_and_ingest_documents_background(session_id, documents, url, "web", url=url)
    except Exception as e:
        print(f"\033[91m× Failed to ingest web page from URL '{url}' for session {session_id}: {str(e)[:100]}...\033[0m")
        logger.error(f"Failed to ingest web page from URL '{url}' for session {session_id}: {e}", exc_info=True)

@app.delete("/remove_vectors", response_model=DeleteResponse)
async def remove_vectors(
    source: str = Query(...),
    session_id: str = Query(...)
):
    """Remove vectors associated with a specific source for a session."""

    # Update last activity
    update_last_activity(session_id)
    print(f"\033[95m{'='*70}")
    print(f"REMOVE VECTORS REQUEST - Session: {session_id}")
    print(f"Source: {source}")
    print(f"{'='*70}\033[0m")
    try:
        store = get_or_init_vectorstore(session_id)
        print(f"\033[96m→ Vectorstore contains {len(store.docstore._dict)} documents\033[0m")
        ids_to_delete = []

        # Search through docstore for matching documents
        for doc_id, doc in store.docstore._dict.items():
            if doc.metadata.get("source") == source or doc.metadata.get("url") == source:
                ids_to_delete.append(doc_id)
                print(f"\033[93m→ Found matching document: {doc_id} (source: {doc.metadata.get('source')}, url: {doc.metadata.get('url')})\033[0m")
        if not ids_to_delete:
            print(f"\033[93m! No vectors found for '{source}' in session {session_id}.\033[0m")
            return DeleteResponse(message=f"No vectors found for '{source}' in session {session_id}.")
        print(f"\033[96m→ Preparing to delete {len(ids_to_delete)} vectors...\033[0m")
        with vectorstore_lock:
            store.delete(ids_to_delete)
            store.save_local(get_session_dir(session_id))
            print(f"\033[92m✓ Deleted {len(ids_to_delete)} vectors for '{source}' in session {session_id}.\033[0m")

        # Update hashes file
        current_hashes = load_ingested_hashes(session_id)
        updated_hashes = [h for h in current_hashes if h != hash_content(source)]
        save_ingested_hashes(session_id, updated_hashes)
        print(f"\033[92m✓ Updated hashes file (removed {len(current_hashes) - len(updated_hashes)} hashes)\033[0m")
        return DeleteResponse(message=f"Removed {len(ids_to_delete)} vectors for '{source}' in session {session_id}.")
    except Exception as e:
        print(f"\033[91m× Failed to remove vectors for session {session_id}: {str(e)[:100]}...\033[0m")
        logger.error(f"Failed to remove vectors for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", summary="API Home")
def root():
    """
    Root endpoint providing a welcome message, available endpoints,
    and notes on per-user upload quota.
    """
    print(f"\033[92m✓ Root endpoint accessed\033[0m")
    return {
        "message": "Welcome to the RAG Chatbot API!",
        "per_user_upload_quota_mb": 50,
        "endpoints": {
            "Health Check": "/health",
            "Chat": "/chat",
            "Ingest (file or URL)": "/ingest",
            "Summarize (file or URL)": "/summarize",
            "Remove Vectors": "/remove_vectors?source=<source>",
            "Remove All Vectors": "/remove_all_vectors",
            "Docs": "/docs"
        }
    }

@app.post("/summarize", response_model=SummarizeResponse, summary="Summarize a PDF Document or Web Page")
async def summarize_endpoint(
    session_id: str = Query(...),  # Add session_id parameter
    file: Optional[UploadFile] = File(None, description="The PDF file to summarize."),
    url: Optional[HttpUrl] = Form(None, description="The URL of the web page to summarize.")
):
    """
    Uploads a PDF file or provides a web page URL and generates a concise summary of its content.
    This does not ingest the content into the vector store.
    Only one of `file` or `url` should be provided.
    """

    # Update last activity
    update_last_activity(session_id)
    print(f"\033[95m{'='*70}")
    print(f"SUMMARIZE REQUEST - Session: {session_id}")
    print(f"{'='*70}\033[0m")
    if not file and not url:
        print(f"\033[91m× Error: Either a PDF file or a web page URL must be provided for summarization.\033[0m")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either a PDF file or a web page URL must be provided for summarization.")
    if file and url:
        print(f"\033[91m× Error: Cannot provide both a PDF file and a URL for summarization. Please provide only one.\033[0m")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot provide both a PDF file and a URL for summarization. Please provide only one.")
    all_text = ""
    source_name = ""
    if file:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            print(f"\033[91m× Error: Only PDF files are supported for file summarization.\033[0m")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are supported for file summarization.")

        # Check file size incrementally
        content = b""
        chunk_size = 1024 * 256  # 256KB chunks
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            content += chunk
            if len(content) > Config.MAX_UPLOAD_FILE_SIZE:
                print(f"\033[91m× Error: File too large. Maximum size is {Config.MAX_UPLOAD_FILE_SIZE / (1024 * 1024):.0f} MB.\033[0m")
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Maximum size is {Config.MAX_UPLOAD_FILE_SIZE / (1024 * 1024):.0f} MB."
                )
        if len(content) == 0:
            print(f"\033[91m× Error: Uploaded file is empty.\033[0m")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")
        print(f"\033[96m→ Processing PDF file for summarization: {file.filename}\033[0m")
        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            print(f"\033[96m→ Temporary file created: {tmp_file_path}\033[0m")
            loader = PyPDFLoader(tmp_file_path)
            print(f"\033[96m→ Loading PDF document...\033[0m")
            pages = loader.load()
            if not pages:
                print(f"\033[91m× Error: The PDF appears to be empty or could not be read.\033[0m")
                return SummarizeResponse(summary="The PDF appears to be empty or could not be read.")
            print(f"\033[92m✓ Loaded {len(pages)} pages from PDF\033[0m")
            all_text = " ".join([p.page_content for p in pages])
            source_name = file.filename
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                print(f"\033[93m→ Cleaned up temporary file: {tmp_file_path}\033[0m")
    elif url:
        url_str = str(url)
        source_name = url_str
        print(f"\033[96m→ Processing URL for summarization: {url_str}\033[0m")
        try:
            loader = WebBaseLoader(url_str)
            print(f"\033[96m→ Loading web content from {url_str}...\033[0m")
            documents = loader.load()
            if not documents:
                print(f"\033[91m× Error: Could not load content from the provided URL.\033[0m")
                return SummarizeResponse(summary="Could not load content from the provided URL.")
            print(f"\033[92m✓ Loaded {len(documents)} document fragments\033[0m")
            # Combine all content from multiple documents loaded by WebBaseLoader
            combined_html_content = " ".join([doc.page_content for doc in documents])
            all_text = clean_web_content(combined_html_content)  # Clean the combined content
        except Exception as e:
            print(f"\033[91m× Error loading web content from URL '{url_str}' for summarization: {str(e)[:100]}...\033[0m")
            logger.error(f"Error loading web content from URL '{url_str}' for summarization: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to load web page content for summarization: {e}")
    if not all_text:
        print(f"\033[91m× Error: No content found to summarize.\033[0m")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No content found to summarize.")

    # Ensure input to summarization model is not too long
    truncated_text = all_text[:Config.MAX_SUMMARY_INPUT_LENGTH]
    if len(all_text) > Config.MAX_SUMMARY_INPUT_LENGTH:
        print(f"\033[93m! Summarization input for {source_name} truncated from {len(all_text)} to {Config.MAX_SUMMARY_INPUT_LENGTH} characters.\033[0m")
        logger.warning(f"Summarization input for {source_name} truncated from {len(all_text)} to {Config.MAX_SUMMARY_INPUT_LENGTH} characters.")
    print(f"\033[96m→ Starting summarization for {source_name} (effective length: {len(truncated_text)}).\033[0m")
    summary_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", """You are an expert summarization AI. Create a concise, accurate, and informative summary of the provided document content.
            Guidelines:
            1. Identify the main topic and key points
            2. Focus on the most important information
            3. Maintain the original meaning and context
            4. Use clear and concise language
            5. Structure the summary logically
            6. Keep it brief but comprehensive"""),
            ("human", "Summarize the following content in brief:\n{text_content}")
        ]
    )
    # Get session temperature for summarization
    temperature = get_session_temperature(session_id)
    summarization_chain = {"text_content": RunnablePassthrough()} | summary_prompt_template | create_llm(temperature) | RunnableLambda(lambda x: x.content)
    logger.info(f"Starting summarization for {source_name} (effective length: {len(truncated_text)}).")
    start_time = time.time()
    summary_text = await summarization_chain.ainvoke(truncated_text)
    execution_time = time.time() - start_time
    print(f"\033[92m✓ Summarization complete for {source_name} ({len(summary_text)} characters) in {execution_time:.2f}s.\033[0m")
    logger.info(f"Summarization complete for {source_name}.")
    return SummarizeResponse(summary=summary_text)

# --- Remove ALL Vectors Endpoint ---
@app.delete("/remove_all_vectors", response_model=DeleteResponse)
async def remove_all_vectors(session_id: str = Query(...)):
    """Remove all vectors for a specific session."""

    # Update last activity
    update_last_activity(session_id)
    print(f"\033[95m{'='*70}")
    print(f"REMOVE ALL VECTORS REQUEST - Session: {session_id}")
    print(f"{'='*70}\033[0m")
    try:
        store = get_or_init_vectorstore(session_id)

        # Get all valid document IDs from the docstore
        all_doc_ids = list(store.docstore._dict.keys())
        print(f"\033[96m→ Vectorstore contains {len(all_doc_ids)} documents to remove\033[0m")
        if not all_doc_ids:
            print(f"\033[93m! No vectors found in session {session_id}.\033[0m")
            return DeleteResponse(message=f"No vectors found in session {session_id}.")
        with vectorstore_lock:

            # Delete using the document store IDs
            store.delete(all_doc_ids)
            store.save_local(get_session_dir(session_id))
            print(f"\033[92m✓ Removed all ({len(all_doc_ids)}) vectors from session {session_id}.\033[0m")

        # Wipe ingested hashes
        save_ingested_hashes(session_id, [])
        print(f"\033[92m✓ Cleared ingested hashes for session {session_id}.\033[0m")
        logger.info(f"Removed all ({len(all_doc_ids)}) vectors from session {session_id}.")
        return DeleteResponse(message=f"Removed all ({len(all_doc_ids)}) vectors from session {session_id}.")
    except Exception as e:
        print(f"\033[91m× Failed to remove all vectors for session {session_id}: {str(e)[:100]}...\033[0m")
        logger.error(f"Failed to remove all vectors for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to remove all vectors: {e}")

# --- Settings Endpoint ---
@app.get("/settings", response_model=SettingsResponse)
async def get_settings(session_id: str = Query(...)):
    """Get current settings for the session."""
    temperature = get_session_temperature(session_id)
    return SettingsResponse(
        temperature=temperature,
        chunk_size=Config.CHUNK_SIZE,
        retriever_k=Config.RETRIEVER_K
    )

@app.post("/settings")
async def update_settings(
    session_id: str = Query(...),
    temperature: Optional[float] = None
):
    """Update session-specific settings."""
    if temperature is not None:
        if temperature < Config.MIN_TEMPERATURE or temperature > Config.MAX_TEMPERATURE:
            raise HTTPException(
                status_code=400, 
                detail=f"Temperature must be between {Config.MIN_TEMPERATURE} and {Config.MAX_TEMPERATURE}"
            )
        # Update the session temperature
        new_temp = set_session_temperature(session_id, temperature)
        print(f"\033[92m✓ Session {session_id} temperature updated to {new_temp:.2f}\033[0m")
    return {"message": "Settings updated successfully", "temperature": get_session_temperature(session_id)}


# Add this endpoint to your FastAPI app (typically near other endpoint definitions)
@app.post("/switch_model")
async def switch_model(
    quantized: bool = Form(..., description="Whether to use quantized model"),
    session_id: str = Query(...)
):
    """Switch between quantized and regular model."""
    try:
        embeddings.set_quantized(quantized)
        logger.info(f"Session {session_id} switched to {'quantized' if quantized else 'regular'} model")
        return {"message": f"Switched to {'quantized' if quantized else 'regular'} model"}
    except Exception as e:
        logger.error(f"Failed to switch model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))    

# --- Main entry point ---
def run_fastapi():
    """Run FastAPI server with port conflict handling"""
    port = 8000
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            print(f"\033[95m{'='*50}")
            print(f"STARTING FASTAPI SERVER ON PORT {port}")
            print(f"{'='*50}\033[0m")
            logger.info(f"Trying to start server on port {port}...")
            # Pass the app instance directly instead of string reference
            uvicorn.run(app, host="0.0.0.0", port=port, reload=False, log_level="info")
            return  # If successful, exit the function
        except Exception as e:
            if "address already in use" in str(e).lower() or "only one usage" in str(e).lower():
                print(f"\033[93m! Port {port} is already in use. Trying port {port+1}...\033[0m")
                logger.warning(f"Port {port} is already in use. Trying port {port+1}...")
                port += 1
            else:
                print(f"\033[91m× Error starting server: {str(e)[:100]}...\033[0m")
                logger.error(f"Error starting server: {e}")
                raise
    print(f"\033[91m× Failed to start server after {max_attempts} attempts\033[0m")
    logger.error(f"Failed to start server after {max_attempts} attempts")
    raise Exception(f"Could not find an available port between 8000 and {8000 + max_attempts - 1}")

def run_streamlit():
    print(f"\033[92m✓ Starting Streamlit app...\033[0m")

    # Make sure your streamlit_app.py is updated to interact with the new /ingest endpoint
    subprocess.Popen(["streamlit", "run", "rag_pdfchatbot_frontend/app.py"])

if __name__ == "__main__":
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    print(f"\033[96m→ Giving FastAPI server 5 seconds to boot up...\033[0m")
    logger.info("Giving FastAPI server 5 seconds to boot up...")
    time.sleep(5) 
    print(f"\033[92m✓ Starting Streamlit app...\033[0m")
    logger.info("Starting Streamlit app...")
    run_streamlit()

    # The main thread will join the FastAPI thread, keeping the process alive
    fastapi_thread.join()

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)    