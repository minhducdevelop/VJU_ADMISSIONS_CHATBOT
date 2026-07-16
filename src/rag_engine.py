import logging
from typing import List, Dict
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma

from src.config import settings
from src.database import history_manager

logger = logging.getLogger("admissions_chatbot.rag_engine")
logging.basicConfig(level=logging.INFO)

class RAGEngine:
    def __init__(self):
        self._vector_store = None
        self._llm = None
        self._embeddings = None

    def _init_components(self):
        """Lazy load components so API key validation happens at runtime."""
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not configured. Please set the GEMINI_API_KEY "
                "environment variable or add it to your .env file."
            )

        if not self._embeddings:
            logger.info("Initializing Google Embeddings...")
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=settings.GEMINI_API_KEY
            )

        if not self._vector_store:
            logger.info(f"Connecting to ChromaDB at: {settings.CHROMA_DB_DIR}")
            self._vector_store = Chroma(
                persist_directory=settings.CHROMA_DB_DIR,
                embedding_function=self._embeddings
            )

        if not self._llm:
            logger.info("Initializing Gemini 1.5 Flash LLM...")
            # Low temperature to ensure factual replies based on context
            self._llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.15
            )

    def query(self, session_id: str, user_query: str) -> str:
        """
        Retrieves relevant documents, formats prompt with context and history,
        calls Gemini 1.5 Flash API, and updates conversation history.
        """
        # Ensure all components are loaded
        try:
            self._init_components()
        except ValueError as ve:
            logger.error(str(ve))
            return f"Lỗi hệ thống: {str(ve)}"
        except Exception as e:
            logger.error(f"Error initializing RAG components: {e}")
            return "Lỗi hệ thống: Không thể kết nối với dịch vụ AI hoặc cơ sở dữ liệu vector."

        # 1. Similarity Search
        logger.info(f"Querying ChromaDB for: '{user_query}'")
        retrieved_docs = []
        try:
            # Get top 4 matching chunks
            retrieved_docs = self._vector_store.similarity_search(user_query, k=4)
        except Exception as e:
            logger.error(f"Error during ChromaDB similarity search: {e}")
            # Non-blocking: continue without vector context, relying on general guidelines

        context = ""
        if retrieved_docs:
            context = "\n---\n".join([doc.page_content for doc in retrieved_docs])
            logger.info(f"Retrieved {len(retrieved_docs)} relevant context blocks from ChromaDB.")
        else:
            logger.warning("No relevant context blocks found in ChromaDB.")

        # 2. Get session chat history (last 3 turns / 6 messages)
        history_list = history_manager.get_history(session_id)
        history_str = ""
        if history_list:
            history_str = "\n".join([
                f"{'Thí sinh' if msg['role'] == 'user' else 'Trợ lý'}: {msg['content']}"
                for msg in history_list
            ])
            logger.info(f"Retrieved chat history for session: {session_id} ({len(history_list)} messages).")
        else:
            history_str = "(Không có lịch sử trò chuyện trước đó)"

        # 3. Build the prompt
        prompt = self._build_prompt(context, history_str, user_query)

        # 4. Invoke LLM
        logger.info("Calling Gemini API...")
        try:
            response = self._llm.invoke(prompt)
            answer = response.content
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return "Lỗi hệ thống: Không thể kết nối tới Google Gemini API. Vui lòng kiểm tra API Key và thử lại."

        # 5. Update Chat History in Cache (Redis / In-memory)
        history_manager.add_message(session_id, "user", user_query)
        history_manager.add_message(session_id, "assistant", answer)

        return answer

    def _build_prompt(self, context: str, history: str, query: str) -> str:
        """Helper to construct the prompt with explicit instruction constraints."""
        system_instruction = (
            "Bạn là Trợ lý Tuyển sinh ảo thông minh, thân thiện và lịch sự của Trường Đại học Việt Nhật (VJU), Đại học Quốc gia Hà Nội.\n"
            "Nhiệm vụ của bạn là trả lời các câu hỏi tuyển sinh của thí sinh một cách chính xác dựa trên thông tin chính thức được cung cấp dưới đây.\n\n"
            "QUY TẮC QUAN TRỌNG:\n"
            "1. Chỉ trả lời dựa trên thông tin có trong phần 'Ngữ cảnh tuyển sinh' dưới đây.\n"
            "2. Nếu thông tin không có trong ngữ cảnh tuyển sinh hoặc bạn không chắc chắn, hãy trả lời lịch sự là thông tin hiện tại chưa được cập nhật đầy đủ và hướng dẫn thí sinh liên hệ với Ban Tuyển sinh của VJU qua hotline (+84) 966954736 hoặc email tuyển sinh (nm.phuong@vju.ac.vn) để được hỗ trợ chính xác nhất.\n"
            "3. Không tự ý bịa đặt thông tin, ngày tháng, điểm số hay chính sách học phí nằm ngoài ngữ cảnh.\n"
            "4. Định dạng câu trả lời rõ ràng, sử dụng gạch đầu dòng và xuống dòng hợp lý để dễ đọc.\n"
            "5. Luôn giữ thái độ tôn trọng, hỗ trợ và xưng hô phù hợp (ví dụ: 'Trợ lý tuyển sinh VJU', 'thí sinh/bạn')."
        )

        prompt = f"""{system_instruction}

=========================================
NGỮ CẢNH TUYỂN SINH CHÍNH THỨC:
{context if context else "Không có ngữ cảnh phù hợp được tìm thấy."}
=========================================

LỊCH SỬ HỘI THOẠI GẦN ĐÂY (Sử dụng để hiểu ngữ cảnh của cuộc đối thoại):
{history}

=========================================
CÂU HỎI MỚI CỦA THÍ SINH:
"{query}"

Hãy trả lời câu hỏi mới này một cách chi tiết và chính xác nhất dựa vào ngữ cảnh tuyển sinh trên:
"""
        return prompt

# Global instance of RAGEngine
rag_engine = RAGEngine()
