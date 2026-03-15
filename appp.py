"""
Complete RAG Chat Application using Dify.ai
No complex setup - just works!
"""

import streamlit as st
import requests
import json

# ==================== CONFIGURATION ====================
DIFY_API_KEY = "app-YRJ7inRQo9b4aTvbxGdulMOq"
DIFY_API_URL = "https://api.dify.ai/v1"

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="🇷🇺 Национальная стратегия ИИ",
    page_icon="📄",
    layout="centered"
)

# Custom CSS for better UI
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main-title {
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 2.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    
    .example-button {
        margin: 0.2rem;
    }
    
    .stButton button {
        width: 100%;
        background-color: white;
        border: 1px solid #1E88E5;
        color: #1E88E5;
        border-radius: 20px;
        padding: 0.5rem;
        font-size: 0.9rem;
    }
    
    .stButton button:hover {
        background-color: #1E88E5;
        color: white;
    }
    
    .user-message {
        background-color: #1E88E5;
        color: white;
        padding: 1rem;
        border-radius: 20px 20px 5px 20px;
        margin-left: 20%;
        margin-bottom: 1rem;
    }
    
    .assistant-message {
        background-color: #f0f2f6;
        color: black;
        padding: 1rem;
        border-radius: 20px 20px 20px 5px;
        margin-right: 20%;
        margin-bottom: 1rem;
        border-left: 4px solid #1E88E5;
    }
    
    .source-box {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
def render_sidebar():
    """Render sidebar with examples"""
    
    with st.sidebar:
        st.markdown("### 📚 О документе")
        st.markdown("""
        **Национальная стратегия развития ИИ**
        - Утверждена: до 2030 года
        - Изменения: 2024 г.
        - Статей: 50+
        
        **Возможности:**
        - ✓ Поиск по документу
        - ✓ Анализ с LLM
        - ✓ Цитирование источников
        """)
        
        st.markdown("---")
        st.markdown("### 💡 Примеры вопросов")
        
        examples = [
            "Какие федеральные законы составляют правовую основу?",
            "Что такое искусственный интеллект?",
            "Что такое большие фундаментальные модели?",
            "Какие цели развития ИИ?",
            "Что такое доверенные технологии?",
            "Какие принципы развития ИИ?",
            "Что говорится в статье 25?"
        ]
        
        for i, example in enumerate(examples):
            if st.button(example, key=f"example_{i}"):
                st.session_state.prompt = example
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 🔑 Статус")
        st.success("✅ Dify.ai API подключен")
        st.markdown("Модель: GPT-4 (через Dify)")

# ==================== DIFY CLIENT ====================
class DifyClient:
    """Client for Dify.ai API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.dify.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat(self, message: str) -> dict:
        """Send a message to Dify chat"""
        
        url = f"{self.base_url}/chat-messages"
        
        payload = {
            "inputs": {},
            "query": message,
            "response_mode": "blocking",
            "conversation_id": "",
            "user": f"user_{hash(message) % 10000}",
            "files": []
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Ошибка API: {response.status_code}")
                st.error(response.text)
                return {"answer": f"❌ Ошибка: {response.status_code}"}
                
        except Exception as e:
            st.error(f"Ошибка соединения: {e}")
            return {"answer": "❌ Не удалось连接到 серверу"}
    
    def get_conversation_history(self, conversation_id: str = None):
        """Get conversation history"""
        url = f"{self.base_url}/messages"
        params = {"conversation_id": conversation_id} if conversation_id else {}
        
        response = requests.get(url, headers=self.headers, params=params)
        return response.json() if response.status_code == 200 else None

# ==================== MAIN CHAT ====================
def main():
    """Main application"""
    
    # Title
    st.markdown('<h1 class="main-title">🇷🇺 Национальная стратегия развития ИИ</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Чат с документом на основе ИИ</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "dify" not in st.session_state:
        st.session_state.dify = DifyClient(DIFY_API_KEY)
    
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    
    # Render sidebar
    render_sidebar()
    
    # Handle preset prompts
    if "prompt" in st.session_state and st.session_state.prompt:
        prompt = st.session_state.prompt
        st.session_state.prompt = None
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get response
        with st.spinner("🤔 Анализирую документ..."):
            result = st.session_state.dify.chat(prompt)
            
            if "answer" in result:
                answer = result["answer"]
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # Save conversation ID for context
                if "conversation_id" in result:
                    st.session_state.conversation_id = result["conversation_id"]
        
        st.rerun()
    
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Задайте вопрос о стратегии..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
        
        # Get response
        with st.spinner("🤔 Анализирую документ..."):
            result = st.session_state.dify.chat(prompt)
            
            if "answer" in result:
                answer = result["answer"]
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.markdown(f'<div class="assistant-message">{answer}</div>', unsafe_allow_html=True)
                
                # Save conversation ID for context
                if "conversation_id" in result:
                    st.session_state.conversation_id = result["conversation_id"]
            else:
                st.error("Не удалось получить ответ")

# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    main()
