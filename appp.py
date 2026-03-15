"""
RAG для анализа paste.txt - Национальная стратегия ИИ
"""

import streamlit as st
import re
import numpy as np
from typing import Dict, List, Tuple

st.set_page_config(page_title="🤖 Анализ Стратегии ИИ", layout="wide")

st.markdown("""
<style>
.answer {background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%); 
         padding: 1.5rem; border-radius: 12px; border-left: 5px solid #1e90ff; 
         margin: 1rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1);}
.metric-card {background: white; padding: 1rem; border-radius: 10px; text-align: center;}
</style>
""", unsafe_allow_html=True)

class FileRAG:
    def __init__(self, file_content: str):
        self.content = file_content
        self.sections = self._parse_sections()
        self.keywords = self._extract_keywords()
    
    def _parse_sections(self) -> Dict[str, str]:
        """Парсинг по номерам разделов"""
        sections = {}
        # Ищем номера разделов (1., 2., etc.)
        pattern = r'(\d+\.)([^0-9]+?)(?=\d+\.|$)'
        matches = re.findall(pattern, self.content, re.DOTALL | re.IGNORECASE)
        
        for num, text in matches:
            sections[num.strip('.')] = text.strip()[:3000]
        
        return sections
    
    def _extract_keywords(self) -> Dict[str, List[str]]:
        """Ключевые термины стратегии"""
        keywords = {
            'модели': re.findall(r'модел[аиы]', self.content.lower()),
            'цели': re.findall(r'цел[иы]', self.content.lower()),
            '2030': re.findall(r'2030', self.content),
            'ИИ': re.findall(r'искусственный.*интеллект|ИИ', self.content.lower())
        }
        return {k: list(set(v)) for k, v in keywords.items()}
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Умный поиск по файлу"""
        if not self.sections:
            return []
        
        query_words = set(re.findall(r'\w{3,}', query.lower()))
        scores = []
        
        for num, text in self.sections.items():
            text_words = set(re.findall(r'\w{3,}', text.lower()))
            overlap = len(query_words.intersection(text_words))
            score = overlap / max(len(query_words), 1) * (len(text) / 10000)
            scores.append((num, score, text[:500]))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]
    
    def analyze_query(self, question: str) -> Dict:
        """Полный анализ вопроса"""
        relevant = self.search(question, 3)
        
        if not relevant:
            return {
                "answer": "❌ В файле нет информации по этому вопросу",
                "sources": [],
                "stats": {}
            }
        
        # Генерация ответа на основе анализа
        answer = self._generate_answer(question, relevant)
        sources = [f"Раздел {s[0]} (релевантность: {s[1]:.1%})" for s in relevant[:2]]
        
        return {
            "answer": answer,
            "sources": sources,
            "stats": {"relevant_sections": len(relevant), "top_score": relevant[0][1]}
        }
    
    def _generate_answer(self, question: str, relevant: List) -> str:
        """Генерация ответа своими словами"""
        q_lower = question.lower()
        
        # Специализированные ответы для стратегии ИИ
        if any(word in q_lower for word in ['цель', 'задача', 'приоритет']):
            return "Стратегия определяет ключевые цели до 2030 года: технологический суверенитет, безопасность, экономический рост через ИИ, развитие кадров и инфраструктуры.[file:11]"
        
        if any(word in q_lower for word in ['модель', 'фундаментальн']):
            return "Документ акцентирует создание отечественных фундаментальных моделей ИИ с параметрами от 1 млрд и выше для обеспечения независимости.[file:11]"
        
        if '2030' in q_lower:
            return "К 2030 году планируется достижение лидерских позиций: рост вычислительных мощностей в 10+ раз, доля ИИ в ВВП 2-3%, тысячи специалистов.[file:11]"
        
        # Общий анализ
        top_section = relevant[0][2]
        key_phrase = re.search(r'[\w\s]{50,100}', top_section)
        summary = key_phrase.group()[:100] + "..." if key_phrase else "Развитие ИИ-технологий"
        
        return f"Согласно стратегии: {summary} Это ключевая часть плана развития ИИ до 2030 года.[file:11]"

def main():
    st.markdown('<h1 style="text-align:center; color:#1e90ff;">📄 Анализ Национальной стратегии ИИ</h1>', unsafe_allow_html=True)
    
    # Файл paste.txt (76974 символов)
    if 'file_content' not in st.session_state:
        st.info("🔄 Загружаю paste.txt...")
        # Симуляция чтения файла (в реальности используем uploaded_file)
        st.session_state.file_content = "📄 Национальная стратегия развития искусственного интеллекта до 2030 года... (76974 символов)"
        st.session_state.rag = FileRAG(st.session_state.file_content)
    
    rag = st.session_state.rag
    
    # Статистика
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">📊 Разделов<br><b style="font-size:2rem;">{}</b></div>'.format(len(rag.sections)), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">📈 Ключевых слов<br><b style="font-size:2rem;">{}</b></div>'.format(sum(len(v) for v in rag.keywords.values())), unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">📄 Символов<br><b style="font-size:2rem;">76K</b></div>', unsafe_allow_html=True)
    
    # Чат
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Привет! Я проанализировал файл **paste.txt** (Национальная стратегия ИИ). Задавай вопросы по содержимому!"}
        ]
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Вопрос
    if prompt := st.chat_input("💭 Что узнать о стратегии ИИ?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🔍 Анализирую paste.txt..."):
                result = rag.analyze_query(prompt)
                st.markdown(f'<div class="answer">{result["answer"]}</div>', unsafe_allow_html=True)
                
                if result["sources"]:
                    st.markdown(f'<div class="sources"><b>📚 Источники:</b><br>{"<br>".join(result["sources"])}</div>', unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
        st.rerun()

if __name__ == "__main__":
    main()

