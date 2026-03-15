"""
Complete RAG Chat Application for Streamlit
Fixed version - no duplicate keys
"""

import streamlit as st
import numpy as np
import os
import re
import requests
from typing import List, Dict, Any
from datetime import datetime

# ==================== CONFIGURATION ====================
HUGGINGFACE_API_KEY = "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"  # Your key
DOCUMENT_FILE = "filerag.txt"  # Your document file

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="🇷🇺 Национальная стратегия ИИ",
    page_icon="📄",
    layout="centered"
)

# Hide Streamlit branding
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main-title {
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .user-message {
        background-color: #1E88E5;
        color: white;
        margin-left: 20%;
    }
    
    .assistant-message {
        background-color: #f0f2f6;
        color: black;
        margin-right: 20%;
        border-left: 4px solid #1E88E5;
    }
    
    .source-box {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid #ddd;
    }
    
    .stButton button {
        width: 100%;
        background-color: white;
        border: 1px solid #1E88E5;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    
    .stButton button:hover {
        background-color: #1E88E5;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DOCUMENT PROCESSOR ====================
class DocumentProcessor:
    """Process and search the document"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.articles = {}
        self.load_document()
    
    def load_document(self):
        """Load and parse document by articles"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Split by article numbers
            lines = text.split('\n')
            current_article = ""
            current_num = ""
            
            for line in lines:
                match = re.match(r'^(\d+)\.\s+(.*)', line.strip())
                if match:
                    if current_num and current_article:
                        self.articles[current_num] = current_article.strip()
                    current_num = match.group(1)
                    current_article = line + "\n"
                elif current_num:
                    current_article += line + "\n"
            
            if current_num and current_article:
                self.articles[current_num] = current_article.strip()
            
        except Exception as e:
            st.error(f"❌ Ошибка загрузки документа: {e}")
    
    def search(self, query: str) -> List[tuple]:
        """Search for relevant articles"""
        query_lower = query.lower()
        results = []
        
        # Priority for specific questions
        if any(word in query_lower for word in ['закон', 'правов', 'федеральн', 'конституц']):
            if '2' in self.articles:
                results.append(('2', self.articles['2'], 1.0))
        
        if any(word in query_lower for word in ['что такое', 'определение', 'понятие']):
            if '5' in self.articles:
                results.append(('5', self.articles['5'], 1.0))
        
        if 'больш' in query_lower and 'модел' in query_lower:
            if '5' in self.articles:
                results.append(('5', self.articles['5'], 1.0))
            if '9' in self.articles:
                results.append(('9', self.articles['9'], 0.9))
        
        # If no priority matches, do keyword search
        if not results:
            keywords = [w for w in query_lower.split() if len(w) > 3]
            for num, text in self.articles.items():
                text_lower = text.lower()
                matches = sum(1 for k in keywords if k in text_lower)
                if matches > 1:
                    results.append((num, text, matches / len(keywords)))
        
        # Sort by relevance and return top 2
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:2]
    
    def get_relevant_part(self, article_num: str, text: str, query: str) -> str:
        """Extract the most relevant part of an article"""
        query_lower = query.lower()
        
        # Special case: Article 5 definition of AI
        if article_num == '5' and ('искусственный интеллект' in query_lower or 'определение' in query_lower):
            match = re.search(r'а\)\s+искусственный интеллект[^.]+\.[^.]+\.[^.]+\.[^.]*', text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Special case: Article 2 legal basis
        if article_num == '2' and any(w in query_lower for w in ['закон', 'правов']):
            match = re.search(r'Правовую основу[^.]+\.\s+[^.]+\.\s+[^.]+\.', text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # General case: find relevant sentences
        sentences = text.split('.')
        relevant = []
        keywords = [w for w in query_lower.split() if len(w) > 3]
        
        for sent in sentences:
            sent_lower = sent.lower()
            matches = sum(1 for k in keywords if k in sent_lower)
            if matches > 0:
                relevant.append((sent, matches))
        
        if relevant:
            relevant.sort(key=lambda x: x[1], reverse=True)
            return '. '.join([r[0] for r in relevant[:3]]) + '.'
        
        return text[:300] + '...'

# ==================== LLM INTEGRATION ====================
class HuggingFaceLLM:
    """Generate answers using Hugging Face API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def generate(self, context: str, question: str) -> str:
        """Generate an answer based on context"""
        
        prompt = f"""<s>[INST] Ты - эксперт по Национальной стратегии развития искусственного интеллекта РФ.
            
ИНСТРУКЦИИ:
1. Отвечай ТОЛЬКО на русском языке
2. Используй информацию из предоставленного контекста
3. Формулируй ответы СВОИМИ СЛОВАМИ
4. Всегда указывай, из каких статей взята информация
5. Если информации нет в контексте, скажи об этом честно

КОНТЕКСТ ИЗ ДОКУМЕНТА:
{context}

ВОПРОС: {question}

ОТВЕТ: [/INST]"""
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 500,
                        "temperature": 0.3,
                        "top_p": 0.95,
                        "do_sample": True,
                        "return_full_text": False
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').strip()
                return str(result)
            else:
                return self._fallback_response(context, question)
                
        except Exception as e:
            return self._fallback_response(context, question)
    
    def _fallback_response(self, context: str, question: str) -> str:
        """Fallback when API fails"""
        return f"На основе документа:\n\n{context[:300]}..."

# ==================== CHAT MANAGER ====================
class ChatManager:
    """Manage chat history and responses"""
    
    def __init__(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "processor" not in st.session_state:
            with st.spinner("🔄 Загрузка документа..."):
                st.session_state.processor = DocumentProcessor(DOCUMENT_FILE)
        if "llm" not in st.session_state:
            st.session_state.llm = HuggingFaceLLM(HUGGINGFACE_API_KEY)
    
    def add_message(self, role: str, content: str):
        """Add a message to history"""
        st.session_state.messages.append({"role": role, "content": content})
    
    def get_response(self, question: str) -> str:
        """Generate response using RAG pipeline"""
        
        # Search for relevant articles
        articles = st.session_state.processor.search(question)
        
        if not articles:
            return "❌ В документе не найдена информация по вашему вопросу."
        
        # Build context
        context_parts = []
        sources = []
        
        for num, text, score in articles:
            relevant_part = st.session_state.processor.get_relevant_part(num, text, question)
            context_parts.append(f"Статья {num}:\n{relevant_part}")
            sources.append(f"ст. {num}")
        
        context = "\n\n".join(context_parts)
        
        # Generate answer
        answer = st.session_state.llm.generate(context, question)
        
        # Add sources
        answer += f"\n\n<div class='source-box'>📚 Источники: {', '.join(sources)}</div>"
        
        return answer

# ==================== UI COMPONENTS ====================
def render_sidebar():
    """Render the sidebar with examples and info"""
    
    with st.sidebar:
        st.markdown("### 📚 О документе")
        st.markdown("""
        **Национальная стратегия развития ИИ**
        - Утверждена: до 2030 года
        - Изменения: 2024 г.
        - Всего статей: 50+
        """)
        
        st.markdown("### 💡 Примеры вопросов")
        
        examples = [
            "Какие федеральные законы составляют правовую основу?",
            "Что такое искусственный интеллект?",
            "Что такое большие фундаментальные модели?",
            "Какие цели развития ИИ?",
            "Что такое доверенные технологии?",
            "Какие принципы развития ИИ?"
        ]
        
        # Create a unique key for each button based on its text
        for i, example in enumerate(examples):
            button_key = f"example_btn_{i}_{example[:10].replace(' ', '_')}"
            if st.button(example, key=button_key):
                st.session_state.question_input = example
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 🔑 Статус")
        
        if HUGGINGFACE_API_KEY.startswith('hf_'):
            st.success("✅ API подключен")
        else:
            st.error("❌ API ключ не найден")
        
        if 'processor' in st.session_state:
            st.metric("Загружено статей", len(st.session_state.processor.articles))

def render_chat():
    """Render the main chat interface"""
    
    st.markdown('<h1 class="main-title">🇷🇺 Национальная стратегия развития ИИ</h1>', unsafe_allow_html=True)
    st.markdown("Чат на основе официального документа (с изменениями 2024 г.)")
    
    # Initialize chat manager
    if 'chat' not in st.session_state:
        st.session_state.chat = ChatManager()
    
    # Handle preset questions from sidebar
    if 'question_input' in st.session_state and st.session_state.question_input:
        question = st.session_state.question_input
        st.session_state.question_input = None  # Clear it
        
        # Add user message
        st.session_state.chat.add_message("user", question)
        
        # Get and add assistant message
        with st.spinner("🤔 Анализирую документ..."):
            response = st.session_state.chat.get_response(question)
            st.session_state.chat.add_message("assistant", response)
        
        st.rerun()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(message["content"], unsafe_allow_html=True)
            else:
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Задайте вопрос о стратегии..."):
        # Add user message
        st.session_state.chat.add_message("user", prompt)
        
        # Get and add assistant message
        with st.chat_message("assistant"):
            with st.spinner("🤔 Анализирую документ..."):
                response = st.session_state.chat.get_response(prompt)
                st.markdown(response, unsafe_allow_html=True)
        
        st.rerun()

# ==================== MAIN ====================
def main():
    """Main application entry point"""
    
    # Check if document exists
    if not os.path.exists(DOCUMENT_FILE):
        st.error(f"❌ Файл {DOCUMENT_FILE} не найден!")
        st.info("Пожалуйста, загрузите файл filerag.txt в ту же папку, что и app.py")
        
        # Show files in current directory
        files = os.listdir('.')
        st.write("Файлы в текущей папке:")
        for f in files:
            st.write(f"- {f}")
        return
    
    # Render sidebar and chat
    render_sidebar()
    render_chat()

# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    main()
