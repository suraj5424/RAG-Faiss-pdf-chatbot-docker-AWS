import re
import uuid  # Added for session ID
import streamlit as st
import requests
import io
from io import BytesIO
import json
import fitz  # PyMuPDF
from PIL import Image
import time
from pypdf import PdfReader
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from typing import Union
import logging
from css import apply_theme_css
import streamlit.components.v1 as components

import streamlit as st

if "css_enabled" not in st.session_state:
    st.session_state.css_enabled = False


# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# # --- Config ---
# FASTAPI_CHAT_URL = "http://localhost:8000/chat"
# FASTAPI_INGEST_URL = "http://localhost:8000/ingest"
# FASTAPI_HEALTH_URL = "http://localhost:8000/health"
# FASTAPI_SUMMARIZE_URL = "http://localhost:8000/summarize"
# FASTAPI_REMOVE_URL = "http://localhost:8000/remove_vectors"
# FASTAPI_REMOVE_ALL_URL = "http://localhost:8000/remove_all_vectors"
# FASTAPI_SETTINGS_URL = "http://localhost:8000/settings"
# FASTAPI_SWITCH_MODEL_URL = "http://localhost:8000/switch_model"  # New endpoint for model switching
# MAX_FILE_SIZE_MB = 10


# --- Config for Docker deployment ---
FASTAPI_CHAT_URL = "http://backend:8000/chat"
FASTAPI_INGEST_URL = "http://backend:8000/ingest"
FASTAPI_HEALTH_URL = "http://backend:8000/health"
FASTAPI_SUMMARIZE_URL = "http://backend:8000/summarize"
FASTAPI_REMOVE_URL = "http://backend:8000/remove_vectors"
FASTAPI_REMOVE_ALL_URL = "http://backend:8000/remove_all_vectors"
FASTAPI_SETTINGS_URL = "http://backend:8000/settings"
FASTAPI_SWITCH_MODEL_URL = "http://backend:8000/switch_model"  # New endpoint for model switching
MAX_FILE_SIZE_MB = 10

# Set page config with modern theme
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="expanded"
)
import streamlit.components.v1 as components

zoom_scroll_sidebar_css = """
<style>
    html {
        zoom: 67%;
    }

    [data-testid="stSidebar"] {
        width: 250px !important;
    }
</style>

<script>
    // Wait a moment for the page to finish rendering, then scroll
    setTimeout(function() {
        parent.window.scrollTo(0, 200);
    }, 500);  // Delay 500ms
</script>
"""

components.html(zoom_scroll_sidebar_css, height=0)

# --- Session Isolation: Generate unique session ID ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
session_id = st.session_state.session_id

# --- Session State Init ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm your RAG Chatbot. Upload PDFs or ingest web pages and let's start exploring!",
            "timestamp": time.time(),
            "meta": {
                "temperature": st.session_state.get("temperature", 0.5)
            }
        }
    ]

if "uploaded_pdfs" not in st.session_state:
    st.session_state.uploaded_pdfs = []
if "ingested_urls" not in st.session_state:
    st.session_state.ingested_urls = []
if "summary_cache" not in st.session_state:
    st.session_state.summary_cache = {}
if "analytics_data" not in st.session_state:
    st.session_state.analytics_data = {"messages": 0, "uploads": 0, "url_ingestions": 0, "last_ingestion": None}
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = "pdf_uploader_1"
if "chat_input_key" not in st.session_state:
    st.session_state.chat_input_key = 0
if "quantized_model" not in st.session_state:
    st.session_state.quantized_model = False  # Default to non-quantized
if "temperature" not in st.session_state:
    # Fetch initial temperature from backend
    try:
        response = requests.get(f"{FASTAPI_SETTINGS_URL}?session_id={session_id}")
        if response.status_code == 200:
            st.session_state.temperature = response.json()["temperature"]
        else:
            st.session_state.temperature = 0.7  # Default on failure
    except Exception as e:
        logger.error(f"Error fetching temperature: {e}")
        st.session_state.temperature = 0.7

# --- CSS Toggle State ---
if "css_enabled" not in st.session_state:
    st.session_state.css_enabled = True  # Default to enabled

# --- Apply theme CSS conditionally ---
if st.session_state.css_enabled:
    apply_theme_css()

# --- Health Check ---
def check_backend():
    try:
        health = requests.get(FASTAPI_HEALTH_URL, timeout=5)
        return health.status_code == 200
    except:
        return False

# --- Theme Toggle Function ---
def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "neon-dark" else "neon-dark"
    if st.session_state.css_enabled:
        apply_theme_css()

# --- CSS Toggle Function ---
def toggle_css():
    st.session_state.css_enabled = not st.session_state.css_enabled
    if st.session_state.css_enabled:
        apply_theme_css()
    # st.rerun()        

# --- Helper function for ingesting content ---
def ingest_content(content_type: str, data: Union[BytesIO, str], name: str):
    try:
        if content_type == "pdf":
            files = {"file": (name, data.getvalue(), "application/pdf")}
            # Add session_id as query parameter
            response = requests.post(
                FASTAPI_INGEST_URL, 
                files=files,
                params={"session_id": session_id}
            )
            st.session_state.analytics_data["uploads"] += 1
        elif content_type == "url":
            data_payload = {"url": data}
            # Add session_id as query parameter
            response = requests.post(
                FASTAPI_INGEST_URL, 
                data=data_payload,
                params={"session_id": session_id}
            )
            st.session_state.analytics_data["url_ingestions"] += 1
        else:
            st.error("Invalid content type for ingestion.")
            return False
        response.raise_for_status()
        resp_json = response.json()
        st.toast(f"✅ `{name}` ingested successfully!", icon="✅")
        st.session_state.analytics_data["last_ingestion"] = time.time()
        return True
    except requests.exceptions.RequestException as e:
        error_msg = str(e.response.text) if e.response else str(e)
        st.toast(f"❌ Ingestion failed for `{name}`: {error_msg[:100]}...", icon="❌")
        return False
    except Exception as e:
        st.toast(f"❌ Unexpected error: {str(e)[:100]}...", icon="❌")
        return False

# --- Sidebar ---
with st.sidebar:
    st.title("RAG Chatbot")
    st.caption("Your smart research companion, powered by AI.")
    
    # Session ID (hidden by default)
    with st.expander("🔍 Session Info", expanded=False):
        st.code(f"Session ID: {session_id}")
    
    # Backend status display with schedule information
    status_col, refresh_col = st.columns([3, 1])
    with status_col:
        backend_status = check_backend()
        
        if backend_status:
            st.success("✅ Backend Services: 🟢 Online")
            st.caption("AI capabilities are fully operational")
        else:
            st.error("⚠️ Backend Services: 🔴 Offline")
            with st.expander("Why is this happening?", expanded=True):
                st.markdown("""
                **Service Hours (Central European Time):**  
                🕒 *Monday to Saturday:*  
                - AI Services: 7:00 AM – 6:00 PM  
                - GUI interaction: Available 24/7  

                🚫 *Sundays:*  
                - All services offline for maintenance  

                ⏳ *Next Available Window:*  
                Please check back during our operational hours  
                """)
                st.info("The GUI interaction remains available, but AI responses will be limited until services resume")
    
    with refresh_col:
        if st.button("🔄 Refresh", help="Check current status"):
            st.rerun()

    # Main controls tabs
    settings_tab, data_tab, tools_tab = st.tabs(["⚙️ Settings", "📂 Data", "🛠️ Tools"])

    with settings_tab:

        # CSS Toggle Button
        css_option = st.radio(
            "CSS Styling",
            ["With CSS", "Without CSS"],
            index=0 if st.session_state.css_enabled else 1,
            horizontal=True,
            key="css_toggle",
            on_change=toggle_css,
            help="Toggle CSS styling on/off. Disabling CSS can result in better latency and smoother UX, especially in resource-constrained environments. CSS adds visual enhancements but may slightly impact performance due to heavier rendering."
        )

        # Temperature control
        temperature = st.slider(
            "Creativity", 0.0, 1.2, st.session_state.temperature, 0.1,
            help="Higher = more creative, Lower = more focused"
        )
        if temperature != st.session_state.temperature:
            try:
                response = requests.post(
                    f"{FASTAPI_SETTINGS_URL}?session_id={session_id}",
                    json={"temperature": temperature}
                )
                if response.status_code == 200:
                    st.session_state.temperature = temperature
                    st.toast(f"Temperature set to {temperature:.1f}", icon="✅")
            except Exception as e:
                st.toast(f"Error updating temperature: {str(e)[:50]}", icon="❌")

        # Model settings
        model_type = st.radio(
            "Model Type", ["Full-precision", "Quantized"],
            index=1 if st.session_state.quantized_model else 0,
            horizontal=True
        )
        new_quantized = model_type == "Quantized"
        if new_quantized != st.session_state.quantized_model:
            try:
                response = requests.post(
                    FASTAPI_SWITCH_MODEL_URL,
                    data={"quantized": new_quantized},
                    params={"session_id": session_id}
                )
                if response.status_code == 200:
                    st.session_state.quantized_model = new_quantized
                    st.toast(f"Switched to {'quantized' if new_quantized else 'full-precision'} model", icon="✅")
            except Exception as e:
                st.toast(f"Error switching model: {str(e)[:50]}", icon="❌")

    with data_tab:
        # PDF Upload in a compact expander
        with st.expander("📄 Upload PDFs", expanded=True):
            uploaded_files = st.file_uploader(
                "Select PDFs", type="pdf", accept_multiple_files=True,
                key=st.session_state.file_uploader_key
            )
            if uploaded_files:
                for f in uploaded_files:
                    if f.name not in [file.name for file in st.session_state.uploaded_pdfs]:
                        if ingest_content("pdf", f, f.name):
                            st.session_state.uploaded_pdfs.append(f)

        # URL Ingestion in a compact expander
        with st.expander("🌐 Ingest URLs", expanded=True):
            url_to_ingest = st.text_input("Enter URL", key="url_ingest_input", placeholder="https://example.com")
            if st.button("Ingest", key="ingest_btn"):
                if url_to_ingest and url_to_ingest not in st.session_state.ingested_urls:
                    with st.spinner("Ingesting..."):
                        if ingest_content("url", url_to_ingest, url_to_ingest):
                            st.session_state.ingested_urls.append(url_to_ingest)

    with tools_tab:
        # Data management
        st.caption("Data Management")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Chat", help="Reset conversation"):
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": "Hello! How can I help?", 
                    "timestamp": time.time()
                }]
                st.session_state.chat_input_key += 1
        with col2:
            if st.button("Clear All", help="Remove all data"):
                try:
                    requests.delete(FASTAPI_REMOVE_ALL_URL, params={"session_id": session_id})
                    st.session_state.uploaded_pdfs = []
                    st.session_state.ingested_urls = []
                    st.session_state.summary_cache = {}
                    st.toast("All data cleared", icon="✅")
                except Exception as e:
                    st.toast("Failed to clear data", icon="❌")

        # Remove individual sources
        sources = [f.name for f in st.session_state.uploaded_pdfs] + st.session_state.ingested_urls
        if sources:
            selected_source = st.selectbox("Source to remove", sources)
            if st.button("Remove Selected"):
                try:
                    requests.delete(FASTAPI_REMOVE_URL, params={"source": selected_source, "session_id": session_id})
                    st.session_state.uploaded_pdfs = [f for f in st.session_state.uploaded_pdfs if f.name != selected_source]
                    st.session_state.ingested_urls = [url for url in st.session_state.ingested_urls if url != selected_source]
                    st.toast(f"Removed: {selected_source}", icon="✅")
                except Exception as e:
                    st.toast("Failed to remove source", icon="❌")

    st.markdown("---")


with st.sidebar.expander("🔒 Privacy Policy", expanded=False):
    st.markdown("""
    **Data Privacy Notice**  
    This app processes your data securely and does not:
    - Store uploaded files, URLs, or chat history permanently.  
    - Share your data with third parties.  
    - Use cookies or tracking beyond the current session.  

    All data is cleared when you close the browser tab or refresh the tab. Avoid uploading personal data. 
    """)
    

with st.sidebar.expander("🧰 Technical Overview", expanded=False):
    st.markdown("""
**Technical Showcase**  
Built with:  
- **Streamlit** (Frontend) | **FastAPI** (Backend) | **PyMuPDF/Fitz** (PDF Processing)  
- **RAG Architecture** (Retrieval-Augmented Generation)  
- **Session-State Management** (Ephemeral data handling)  
- **Async API Integrations** (Low-latency document processing)  

**Key Features:**  
✅ **Document Intelligence**  
- PDF text extraction & semantic search  
- Multi-page preview with PyMuPDF rendering  
- Context-aware Q&A with source attribution  

✅ **Web Content Processing**  
- URL ingestion with metadata extraction  
- Content summarization via NLP pipelines  

✅ **Customizable AI**  
- Dynamic temperature control (0.0–1.5 range)  
- Model quantization toggle (FP32 vs. INT8)  
- Isolated session configurations  

✅ **Data Portability**  
- JSON/Markdown/PDF export generation  
- Client-side data processing (zero server storage)  

**Architecture Highlights:**  
⚡ Persistent session isolation via UUIDv4  
⚡ CSS-injected theming system  
⚡ Analytics instrumentation  
⚡ Memory-efficient file handling (<10MB)  
""")


# --- Main Content ---
st.markdown("""
    <div style="text-align:center; padding:20px 0;">
        <h1 style='color: #1E88E5; margin-bottom:8px;'>RAG Chatbot Assistant</h1>
        <p style='font-size:1.2rem; color: #455A64; max-width:800px; margin:0 auto;'>
            Unlock insights from your documents and web content with AI-powered analysis
        </p>
    </div>
""", unsafe_allow_html=True)
# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Chat",
    "📄 Documents",
    "🌐 Web Content",
    "📈 Analytics",
    "📥 Export"
])

# --- Tab 1: Chat ---
with tab1:
    st.subheader("Chat with AI Assistant")
    # Display current temperature
    st.caption(f"Current creativity level: {st.session_state.temperature:.1f}")

    # Chat container
    chat_container = st.container(height=500)
    with chat_container:
        for msg in st.session_state.messages:
            timestamp = time.strftime("%H:%M", time.localtime(msg.get("timestamp", time.time())))
            message_class = "user-message" if msg["role"] == "user" else "assistant-message"

            with st.chat_message(msg["role"]):
                st.markdown(f"<div class='{message_class}'>", unsafe_allow_html=True)
                st.markdown(msg["content"])

                # Show timestamp, temperature, and model for both roles if meta present
                if "meta" in msg and "temperature" in msg["meta"]:
                    temp_info = f"Temp: {msg['meta']['temperature']:.1f}"
                    model_info = f"Model: {msg['meta'].get('model', 'Full-precision')}"
                    st.markdown(
                        f"<div style='text-align: right; font-size: 0.75rem; color: gray;'>"
                        f"{timestamp} | {temp_info} | {model_info}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.caption(timestamp)

                st.markdown("</div>", unsafe_allow_html=True)

    # Chat input with clearable option
    user_query = st.chat_input(
        "Ask about your documents...", 
        key=f"chat_input_{st.session_state.get('chat_input_key', 0)}"
    )

    if user_query:
        # Append user message with meta
        st.session_state.messages.append({
            "role": "user", 
            "content": user_query, 
            "timestamp": time.time(),
            "meta": {
                "temperature": st.session_state.temperature,
                "model": "Quantized" if st.session_state.quantized_model else "Full-precision"
            }
        })

        # Display user message immediately
        with chat_container:
            with st.chat_message("user"):
                st.markdown("<div class='user-message'>", unsafe_allow_html=True)
                st.markdown(user_query)
                model_type = "Quantized" if st.session_state.quantized_model else "Full-precision"
                st.markdown(
                    f"<div style='text-align: right; font-size: 0.75rem; color: gray;'>"
                    f"{time.strftime('%H:%M')} | Temp: {st.session_state.temperature:.1f} | Model: {model_type}</div>",
                    unsafe_allow_html=True
                )
                st.markdown("</div>", unsafe_allow_html=True)


        with st.spinner("Thinking..."):
            try:
                payload = {
                    "query": user_query,
                    "chat_history": [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.messages
                        if msg["role"] in ["user", "assistant"]
                    ],
                    "temperature": st.session_state.temperature
                }

                response = requests.post(
                    FASTAPI_CHAT_URL,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json"},
                    params={"session_id": session_id}
                )
                response.raise_for_status()
                resp = response.json()

                # Sanitize backend temperature lines from response text
                bot_reply = resp.get("response", "Sorry, I couldn't process your request.")
                bot_reply = re.sub(r"\*?Response generated with temperature:.*\*?", "", bot_reply).strip()

                # Add sources if any
                if "retrieved_sources" in resp and resp["retrieved_sources"]:
                    sources = "\n**Sources:**\n" + "\n".join(
                        [f"- {s['source']} (Page {s['page']})" for s in resp["retrieved_sources"]]
                    )
                    bot_reply += sources

                # Clean excessive newlines
                bot_reply = re.sub(r'\n{3,}', '\n\n', bot_reply).strip()

                # Prepare assistant message with meta temperature and model info
                assistant_message = {
                    "role": "assistant",
                    "content": bot_reply,
                    "timestamp": time.time(),
                    "meta": {
                        "temperature": resp.get("temperature", st.session_state.temperature),
                        "model": "Quantized" if st.session_state.quantized_model else "Full-precision"
                    }
                }

            except Exception as e:
                assistant_message = {
                    "role": "assistant",
                    "content": f"⚠️ Error: {str(e)}",
                    "timestamp": time.time(),
                    "meta": {
                        "temperature": st.session_state.temperature,
                        "model": "Quantized" if st.session_state.quantized_model else "Full-precision"
                    }
                }

        # Append assistant message
        st.session_state.messages.append(assistant_message)

        # Display assistant message immediately
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown("<div class='assistant-message'>", unsafe_allow_html=True)
                st.markdown(assistant_message["content"])
                st.markdown(
                    f"<div style='text-align: right; font-size: 0.75rem; color: gray;'>"
                    f"{time.strftime('%H:%M', time.localtime(assistant_message['timestamp']))} | "
                    f"Temp: {assistant_message['meta']['temperature']:.1f}</div>",
                    unsafe_allow_html=True
                )
                st.markdown("</div>", unsafe_allow_html=True)

        # Auto-scroll
        st.rerun()

# --- Tab 2: Document Viewer (PDF) ---
with tab2:
    st.subheader("PDF Documents")
    if not st.session_state.uploaded_pdfs:
        st.info("Upload PDFs using the sidebar to get started")
        # st.image("https://img.icons8.com/?size=100&id=VPthXwCrUAPV&format=png&color=000000", width='stretch')
    else:
        # Document selection
        selected_pdf = st.selectbox(
            "Select a document",
            options=st.session_state.uploaded_pdfs,
            format_func=lambda f: f.name,
            index=0,
            key="document_selector"
        )
        if selected_pdf:
            st.caption(f"Viewing: {selected_pdf.name}")
            # Document tools
            with st.expander("Document Tools", expanded=True):
                search_col, sum_col = st.columns([2, 1])
                with search_col:
                    search_query = st.text_input("Search in document", placeholder="Enter keywords...")
                with sum_col:
                    st.write("")
                    st.write("")
                    summarize_full = st.button("✨ Summarize", width='stretch')
            # PDF viewer
            try:
                pdf_reader = PdfReader(BytesIO(selected_pdf.getvalue()))
                total_pages = len(pdf_reader.pages)
                # Page navigation
                if total_pages > 1:
                    page_num = st.slider("Page", 1, total_pages, 1, key="page_slider")
                else:
                    page_num = 1
                    st.caption("Document has 1 page")
                # PDF display tabs
                img_tab, text_tab = st.tabs(["Visual Preview", "Text Content"])
                with img_tab:
                    pdf_doc = fitz.open(stream=selected_pdf.getvalue(), filetype="pdf")
                    page = pdf_doc.load_page(page_num - 1)
                    pix = page.get_pixmap(dpi=150)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    st.image(img, width='stretch', caption=f"Page {page_num} of {total_pages}")
                with text_tab:
                    try:
                        page_text = pdf_reader.pages[page_num - 1].extract_text() or "No text content"
                        if search_query:
                            highlight_color = '#FFF59D' if st.session_state.get("theme") == 'light' else '#FFD54F'
                            highlighted_text = re.sub(
                                f"({re.escape(search_query)})", 
                                f"<mark style='background-color: {highlight_color};'>\\1</mark>", 
                                page_text, 
                                flags=re.IGNORECASE
                            )
                            st.markdown(highlighted_text, unsafe_allow_html=True)
                        else:
                            st.text_area("Content", page_text, height=300, label_visibility="collapsed")
                    except Exception as e:
                        st.warning(f"Could not extract text: {e}")
                # Summarization
                if summarize_full:
                    with st.spinner("Generating summary..."):
                        try:
                            doc_key = selected_pdf.name
                            cache_key = f"pdf_summary_{doc_key}"
                            if cache_key in st.session_state.summary_cache:
                                summary = st.session_state.summary_cache[cache_key]
                                st.info("Using cached summary")
                            else:
                                pdf_bytes = selected_pdf.getvalue()
                                files = {"file": (selected_pdf.name, pdf_bytes, "application/pdf")}
                                # Add session_id to summarize request
                                response = requests.post(
                                    FASTAPI_SUMMARIZE_URL, 
                                    files=files,
                                    params={"session_id": session_id}
                                )
                                response.raise_for_status()
                                summary = response.json().get("summary", "No summary available")
                                st.session_state.summary_cache[cache_key] = summary
                            st.subheader("Document Summary")
                            st.write(summary)
                        except Exception as e:
                            st.error(f"Error generating summary: {str(e)}")
            except Exception as e:
                st.error(f"Failed to load PDF: {str(e)}")

# --- Tab 3: Web Content Viewer ---
with tab3:
    st.subheader("Web Content")
    if not st.session_state.ingested_urls:
        st.info("Ingest web content using the sidebar")
        # st.image("https://img.icons8.com/?size=100&id=rKxTiRI0A6Ud&format=png&color=000000", width='stretch')
    else:
        # URL selection
        selected_url = st.selectbox(
            "Select web content",
            options=st.session_state.ingested_urls,
            index=0,
            key="url_selector"
        )
        if selected_url:
            st.caption(f"Viewing: {selected_url}")
            # Content tools
            with st.expander("Content Tools", expanded=True):
                if st.button("✨ Summarize Content", width='stretch'):
                    st.session_state["summarize_web"] = True
            # Content display
            cache_key = f"web_content_{selected_url}"
            if cache_key in st.session_state.summary_cache:
                web_content = st.session_state.summary_cache[cache_key]
            else:
                with st.spinner("Loading content..."):
                    try:
                        # Add session_id to summarize request
                        response = requests.post(
                            FASTAPI_SUMMARIZE_URL, 
                            data={"url": selected_url},
                            params={"session_id": session_id}
                        )
                        response.raise_for_status()
                        web_content = response.json().get("summary", "Could not retrieve content")
                        st.session_state.summary_cache[cache_key] = web_content
                    except Exception as e:
                        web_content = f"Error: {str(e)}"
            st.subheader("Content Preview")
            with st.container(height=400):
                st.markdown(web_content, unsafe_allow_html=True)
            # Show summary if requested
            if st.session_state.get("summarize_web"):
                web_summary_cache_key = f"web_summary_{selected_url}"
                if web_summary_cache_key in st.session_state.summary_cache:
                    summary = st.session_state.summary_cache[web_summary_cache_key]
                    st.info("Using cached summary")
                else:
                    with st.spinner("Generating summary..."):
                        try:
                            # Add session_id to summarize request
                            response = requests.post(
                                FASTAPI_SUMMARIZE_URL, 
                                data={"url": selected_url},
                                params={"session_id": session_id}
                            )
                            response.raise_for_status()
                            summary = response.json().get("summary", "No summary available")
                            st.session_state.summary_cache[web_summary_cache_key] = summary
                        except Exception as e:
                            summary = f"Error: {str(e)}"
                st.subheader("Content Summary")
                st.write(summary)
                st.session_state.pop("summarize_web", None)

# --- Tab 4: Analytics & History ---
with tab4:
    st.subheader("Usage Analytics")
    # Metrics cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Chat Messages", st.session_state.analytics_data.get("messages", 0))
    col2.metric("PDF Uploads", st.session_state.analytics_data.get("uploads", 0))
    col3.metric("Web Ingestions", st.session_state.analytics_data.get("url_ingestions", 0))
    if st.session_state.analytics_data.get("last_ingestion"):
        last_ingest = time.strftime("%Y-%m-%d %H:%M", 
                                  time.localtime(st.session_state.analytics_data["last_ingestion"]))
        st.caption(f"Last content ingestion: {last_ingest}")
    st.divider()
    st.subheader("Recent Chat History")
    if not st.session_state.messages:
        st.info("No chat history yet")
    else:
        # Show last 10 messages in expanders
        for msg in reversed(st.session_state.messages[-10:]):
            role = "🤖 Assistant" if msg["role"] == "assistant" else "👤 You"
            timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(msg.get("timestamp", time.time())))
            with st.expander(f"{role} - {timestamp}"):
                st.write(msg["content"])

# --- Tab 5: Export Data ---
with tab5:
    st.subheader("Export Data")
    export_format = st.radio("Export format", ["JSON", "PDF", "Markdown"], horizontal=True)

    def clean_text(text):
        replacements = {'’': "'", '‘': "'", '“': '"', '”': '"', '—': '-', '–': '-', '…': '...'}
        for k, v in replacements.items():
            text = text.replace(k, v)
        # Remove emojis and non-ASCII chars
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        return text

    if export_format == "JSON":
        export_data = {
            "chat_messages": st.session_state.messages,
            "analytics": st.session_state.analytics_data,
            "documents": [f.name for f in st.session_state.uploaded_pdfs],
            "web_content": st.session_state.ingested_urls
        }
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name="rag_export.json",
            mime="application/json",
            width='stretch'
        )

    elif export_format == "PDF":
        def _write_inline_markdown(pdf, text):

            # Replace all instances of "---" with "___"
            text = text.replace('---', '________' * 40)

            # Handle bold **text**, italic *text*, underline __text__
            pattern = re.compile(r'(\*\*.+?\*\*|\*.+?\*|__.+?__)')
            parts = pattern.split(text)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    pdf.set_font("Helvetica", 'B', 10)
                    pdf.write(6, part[2:-2])
                    pdf.set_font("Helvetica", '', 10)
                elif part.startswith('*') and part.endswith('*'):
                    pdf.set_font("Helvetica", 'I', 10)
                    pdf.write(6, part[1:-1])
                    pdf.set_font("Helvetica", '', 10)
                elif part.startswith('__') and part.endswith('__'):
                    pdf.set_font("Helvetica", 'U', 10)
                    pdf.write(6, part[2:-2])
                    pdf.set_font("Helvetica", '', 10)
                else:
                    pdf.write(6, part)

        def write_markdown_to_pdf(pdf, text):
            import re

            lines = text.splitlines()
            for line in lines:
                line = line.rstrip()

                # Headings (# to ######)
                heading_match = re.match(r'^(#{1,6})\s*(.*)', line)
                if heading_match:
                    level = len(heading_match.group(1))
                    content = heading_match.group(2).strip()
                    sizes = {1: 16, 2: 14, 3: 12, 4: 11, 5: 10, 6: 9}
                    font_size = sizes.get(level, 10)
                    pdf.set_font("Helvetica", 'B', font_size)
                    pdf.cell(0, 10, clean_text(content), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.ln(2)
                    continue

                # Ordered list item (e.g. 1. Text)
                ol_match = re.match(r'^(\s*)(\d+)\.\s+(.*)', line)
                if ol_match:
                    indent_spaces = len(ol_match.group(1))
                    number = ol_match.group(2)
                    content = ol_match.group(3)
                    indent = 10 + indent_spaces * 4

                    pdf.set_x(indent)
                    pdf.set_font("Helvetica", 'B', 10)
                    pdf.write(6, f"{number}. ")
                    pdf.set_font("Helvetica", '', 10)
                    _write_inline_markdown(pdf, clean_text(content))
                    pdf.ln(5)
                    continue

                # Unordered list item (- or *)
                ul_match = re.match(r'^(\s*)[-*]\s+(.*)', line)
                if ul_match:
                    indent_spaces = len(ul_match.group(1))
                    content = ul_match.group(2)
                    indent = 15 + indent_spaces * 4

                    pdf.set_x(indent)
                    pdf.set_font("Helvetica", 'B', 10)
                    pdf.write(6, "- ")
                    pdf.set_font("Helvetica", '', 10)
                    _write_inline_markdown(pdf, clean_text(content))
                    pdf.ln(7)
                    continue

                # Normal paragraph text
                if line.strip() == "":
                    pdf.ln(3)
                else:
                    pdf.set_x(10)
                    pdf.set_font("Helvetica", '', 10)
                    _write_inline_markdown(pdf, clean_text(line))
                    pdf.ln(6)

        def generate_pdf_export():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)

            pdf.set_font("Helvetica", 'B', 16)
            pdf.cell(0, 10, "RAG Chatbot Export", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
            pdf.ln(10)

            # Prepare markdown export text (reuse your markdown generator)
            md_export = generate_markdown_export()

            # Write markdown with formatting
            write_markdown_to_pdf(pdf, md_export)

            buffer = io.BytesIO()
            pdf.output(buffer)
            buffer.seek(0)
            return buffer

        def generate_markdown_export():
            md = "# RAG Chatbot Export\n"
            md += "## Chat History\n"
            for msg in st.session_state.messages:
                role = "**Assistant**" if msg["role"] == "assistant" else "**User**"
                content = msg["content"]
                timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(msg.get("timestamp", time.time())))
                md += f"{role} ({timestamp}):\n{content}\n---\n"
            md += "## Analytics\n"
            md += f"- Total Messages: {st.session_state.analytics_data.get('messages', 0)}\n"
            md += f"- PDF Uploads: {st.session_state.analytics_data.get('uploads', 0)}\n"
            md += f"- Web Ingestions: {st.session_state.analytics_data.get('url_ingestions', 0)}\n"
            if st.session_state.analytics_data.get("last_ingestion"):
                last_ingest = time.strftime("%Y-%m-%d %H:%M", time.localtime(st.session_state.analytics_data["last_ingestion"]))
                md += f"- Last Ingestion: {last_ingest}\n"
            if st.session_state.uploaded_pdfs:
                md += "\n## Uploaded Documents\n"
                for doc in st.session_state.uploaded_pdfs:
                    md += f"- {doc.name}\n"
            if st.session_state.ingested_urls:
                md += "\n## Ingested URLs\n"
                for url in st.session_state.ingested_urls:
                    md += f"- [{url}]({url})\n"
            return md

        st.download_button(
            label="📄 Download PDF",
            data=generate_pdf_export(),
            file_name="rag_export.pdf",
            mime="application/pdf",
            width='stretch'
        )

    elif export_format == "Markdown":
        def generate_markdown_export():
            md = "# RAG Chatbot Export\n"
            md += "## Chat History\n"
            for msg in st.session_state.messages:
                role = "**Assistant**" if msg["role"] == "assistant" else "**User**"
                content = clean_text(msg["content"])
                timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(msg.get("timestamp", time.time())))
                md += f"{role} ({timestamp}):\n{content}\n---\n"
            md += "## Analytics\n"
            md += f"- Total Messages: {st.session_state.analytics_data.get('messages', 0)}\n"
            md += f"- PDF Uploads: {st.session_state.analytics_data.get('uploads', 0)}\n"
            md += f"- Web Ingestions: {st.session_state.analytics_data.get('url_ingestions', 0)}\n"
            if st.session_state.analytics_data.get("last_ingestion"):
                last_ingest = time.strftime("%Y-%m-%d %H:%M", time.localtime(st.session_state.analytics_data["last_ingestion"]))
                md += f"- Last Ingestion: {last_ingest}\n"
            if st.session_state.uploaded_pdfs:
                md += "\n## Uploaded Documents\n"
                for doc in st.session_state.uploaded_pdfs:
                    md += f"- {doc.name}\n"
            if st.session_state.ingested_urls:
                md += "\n## Ingested URLs\n"
                for url in st.session_state.ingested_urls:
                    md += f"- [{url}]({url})\n"
            return md

        st.download_button(
            label="📝 Download Markdown",
            data=generate_markdown_export(),
            file_name="rag_export.md",
            mime="text/markdown",
            width='stretch'
        )

# --- Footer ---
def add_footer():
    """Add a thin, responsive footer strip with right-side margin."""
    footer_html = """
    <div class="footer-thin">
        <div class="left">
            🛠️ <strong>RAG Chatbot</strong> by 
            <a href="https://www.linkedin.com/in/suraj5424/" target="_blank">Suraj Varma</a> 👨‍💻
        </div>
        <div class="center">
            📚 Unlock precise answers from your documents and the web.
        </div>
        <div class="right">
            <a href="https://github.com/suraj5424" target="_blank">💻 GitHub</a>
            <a href="https://linkedin.com/in/suraj5424" target="_blank">🔗 LinkedIn</a>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)
add_footer()