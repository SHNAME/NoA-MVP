import streamlit as st
from modules.ingest import ingest_docs  # 만약 ingest_docs 위치가 다르면 경로 맞춰주기

def show_chatbot_page(rag_service):
    """
    app.py에서 호출할 AI 챗봇 전용 페이지 UI 모듈
    """
    st.markdown('<p style="font-size:3rem; text-align:center; margin:0;">🤖</p>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #FF914D; font-family: \'JejuDoldam\', sans-serif;">해말금 AI 비서 대화방</h2>', unsafe_allow_html=True)
    st.caption("태양광 설치 비용, 투자금 회수 기간, 분뇨 처리 원리에 대해 자유롭게 질문해 보세요.")
    st.write("---")

    if "db_initialized" not in st.session_state:
        st.session_state.db_initialized = False

    if not st.session_state.db_initialized:
        current_count = rag_service.count_documents()
        if current_count == 0:
             with st.spinner("문서를 분석 중입니다. 잠시만 기다려주세요..."):
                 saved_count = ingest_docs(rag_service)
                 if saved_count > 0:
                     st.success(f"✅ {saved_count}개의 문서 페이지를 학습했습니다.")
                 else:
                     st.warning("⚠️ docs 폴더에 읽을 수 있는 PDF 문서가 없습니다.")
        st.session_state.db_initialized = True

    if "messages" not in st.session_state:
        st.session_state.messages = [
             {"role": "assistant", "content": "반가워요! 해말금 AI 비서입니다. ☀️\n 프로젝트나 분석 수치에 대해 궁금한 점을 편하게 물어보세요."}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
             st.write(msg["content"])

    if user_query := st.chat_input("궁금한 점을 입력하세요 (예: 설치 비용 얼마야?)"):
        with st.chat_message("user"):
             st.write(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})

        with st.chat_message("assistant"):
             with st.spinner("관련 문서를 확인하고 있습니다..."):
                 try:
                     response = rag_service.ask(user_query)
                 except Exception as e:
                     response = f"죄송합니다. 답변을 생성하는 중 오류가 발생했습니다: {str(e)}"
             st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})