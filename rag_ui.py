import streamlit as st

from modules.rag_service import RagService
from ingest import ingest_docs


st.set_page_config(
    page_title="SolarSludge 챗봇",
    page_icon="🌱",
    layout="centered"
)

st.markdown("""
<style>
    /* 전체 배경 - 따뜻한 베이지 */
    .stApp {
        background-color: #f5f0e8;
    }

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background-color: #e8e0d0;
    }

    /* 헤더 영역 */
    .main-header {
        background: linear-gradient(135deg, #4a7c59, #6a9e72);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        color: white;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin: 8px 0 0 0;
        font-size: 1rem;
        opacity: 0.88;
    }

    /* 채팅 말풍선 - 사용자 */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background-color: #dff0d8;
        border-radius: 16px;
        padding: 4px 8px;
        margin: 6px 0;
    }

    /* 채팅 말풍선 - 어시스턴트 */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 4px 8px;
        margin: 6px 0;
        border: 1px solid #d9d0c0;
        color: #2e2e2e;
    }

    /* 어시스턴트 말풍선 내 텍스트 */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) li,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) span {
        color: #2e2e2e !important;
    }

    /* 입력창 */
    [data-testid="stChatInput"] {
        background-color: #ffffff;
        border-radius: 12px;
        border: 1.5px solid #a0b89a;
    }

    /* 텍스트 전반 */
    .stMarkdown p {
        font-size: 1.05rem;
        line-height: 1.75;
        color: #2e2e2e;
    }

    /* 상태 메시지 */
    .stAlert {
        border-radius: 12px;
    }

    /* 스피너 */
    .stSpinner {
        color: #4a7c59;
    }
</style>
""", unsafe_allow_html=True)


# 헤더
st.markdown("""
<div class="main-header">
    <h1>🌱 SolarSludge 문서 챗봇</h1>
    <p>태양광 잉여전력 기반 슬러지 건조 관련 정부 문서를 검색하고 질문에 답변드립니다.</p>
</div>
""", unsafe_allow_html=True)


@st.cache_resource
def load_rag_service():
    return RagService()


rag_service = load_rag_service()


if "db_initialized" not in st.session_state:
    st.session_state.db_initialized = False

if not st.session_state.db_initialized:
    current_count = rag_service.collection.count()

    if current_count == 0:
        with st.spinner("문서를 불러오는 중입니다. 잠시만 기다려주세요..."):
            saved_count = ingest_docs(rag_service)

        if saved_count == 0:
            st.warning("docs 폴더에 저장할 PDF 문서가 없거나 추출 가능한 텍스트가 없습니다.")
        else:
            st.success(f"✅ 문서 준비 완료 — {saved_count}개 페이지 처리됐습니다.")
    else:
        st.info(f"📂 저장된 문서를 불러왔습니다. (chunk 수: {current_count})")

    st.session_state.db_initialized = True


if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요 👋\n\n저는 가축분뇨 자원화시설, 재생에너지 출력제어 등 관련 정부 문서를 기반으로 답변하는 챗봇입니다.\n\n궁금하신 내용을 편하게 질문해주세요."
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_question = st.chat_input("질문을 입력하세요 (예: 터파기 기준이 뭔가요?)")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner("관련 문서를 찾는 중입니다..."):
            answer = rag_service.ask(user_question)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
