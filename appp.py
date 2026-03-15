import streamlit as st

st.set_page_config(
    page_title="🇷🇺 Национальная стратегия ИИ",
    page_icon="📄",
    layout="wide"
)

# Custom CSS to make the iframe look perfect
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
    
    /* Make the iframe container full height */
    .stApp {
        background-color: white;
    }
    
    iframe {
        border: none;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-title">🇷🇺 Национальная стратегия развития ИИ</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Чат с документом на основе ИИ (встроенный чат Dify)</p>', unsafe_allow_html=True)

# Embed the Dify chatbot
chatbot_url = "https://udify.app/chatbot/Syxg8Vbb7Xk9ZjVA"

st.components.v1.html(
    f"""
    <iframe
        src="{chatbot_url}"
        style="width: 100%; height: 700px; border: none; border-radius: 10px;"
        frameborder="0"
        allow="microphone">
    </iframe>
    """,
    height=720,
    scrolling=False
)

# Optional: Add some information in the sidebar
with st.sidebar:
    st.markdown("### 📚 О документе")
    st.markdown("""
    **Национальная стратегия развития ИИ**
    - Утверждена: до 2030 года
    - Изменения: 2024 г.
    - Статей: 50+
    
    **Возможности чата:**
    - ✓ Задавайте вопросы на русском
    - ✓ Получайте ответы с источниками
    - ✓ Сохраняется история диалога
    """)
    
    st.markdown("---")
    st.markdown("### 💡 Примеры вопросов")
    examples = [
        "Какие федеральные законы составляют правовую основу?",
        "Что такое искусственный интеллект?",
        "Что такое большие фундаментальные модели?",
        "Какие цели развития ИИ?"
    ]
    for ex in examples:
        st.info(f"💬 {ex}")
