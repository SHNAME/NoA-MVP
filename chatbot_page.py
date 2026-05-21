import streamlit as st
import random
from ingest import ingest_docs

# ── 질문 뱅크 ────────────────────────────────────────────────────────────────
QUESTION_BANK = [
    # 보조금
    {"text": "분뇨 처리 보조금 얼마나 받을 수 있어요?",       "category": "보조금"},
    {"text": "보조금이랑 융자 같이 받을 수 있어요?",           "category": "보조금"},
    {"text": "공동자원화시설은 지원금이 얼마예요?",            "category": "보조금"},
    # 신청방법
    {"text": "보조금 신청은 어디에 가서 해요?",                "category": "신청방법"},
    {"text": "신청할 때 어떤 서류가 필요해요?",                "category": "신청방법"},
    {"text": "신청하면 어떤 절차로 진행돼요?",                 "category": "신청방법"},
    {"text": "선정되면 어떻게 알려줘요?",                      "category": "신청방법"},
    {"text": "우리 농장이 신청 자격이 되는지 어떻게 알아요?",  "category": "신청방법"},
    # 시설장비
    {"text": "악취 줄이는 시설도 보조금 나와요?",              "category": "시설장비"},
    {"text": "바이오가스 만드는 시설도 지원받을 수 있어요?",   "category": "시설장비"},
    {"text": "정화 처리 시설도 보조 대상이에요?",              "category": "시설장비"},
    # 사후관리
    {"text": "보조금 받은 뒤에 지켜야 할 게 있어요?",          "category": "사후관리"},
    {"text": "보조금 받은 장비를 팔면 어떻게 돼요?",           "category": "사후관리"},
    {"text": "사업 도중에 그만두면 어떻게 돼요?",              "category": "사후관리"},
    {"text": "잘못 받으면 어떤 불이익이 있어요?",              "category": "사후관리"},
    {"text": "시설 유지·관리 의무가 몇 년이나 돼요?",          "category": "사후관리"},
    # 환경/자원화
    {"text": "분뇨를 퇴비로 만들면 돈이 돼요?",               "category": "환경"},
    {"text": "자연순환농업 사업이 뭐예요?",                    "category": "환경"},
    {"text": "온실가스 줄이면 지원받을 수 있어요?",            "category": "환경"},
    {"text": "바이오차가 뭐고 지원이 돼요?",                   "category": "환경"},
]

# 카테고리별 관련 카테고리 (답변 후 이 순서로 관련 질문 채움)
RELATED_CATEGORIES = {
    "보조금":   ["신청방법", "시설장비", "사후관리", "환경"],
    "신청방법": ["보조금",   "시설장비", "사후관리"],
    "시설장비": ["보조금",   "신청방법", "환경",     "사후관리"],
    "사후관리": ["보조금",   "신청방법", "시설장비"],
    "환경":     ["시설장비", "보조금",   "신청방법"],
}

CATEGORY_EMOJI = {
    "보조금":   "💰",
    "신청방법": "📋",
    "시설장비": "🏭",
    "사후관리": "📌",
    "환경":     "🌱",
}


def _pick_related(current_category: str, exclude: set, n: int = 5) -> list:
    """현재 카테고리 기반으로 관련 질문 n개 선택"""
    related_cats = RELATED_CATEGORIES.get(current_category, list(RELATED_CATEGORIES.keys()))

    # 현재 카테고리 질문 2개 + 관련 카테고리 질문 3개
    same_pool    = [q for q in QUESTION_BANK if q["category"] == current_category and q["text"] not in exclude]
    related_pool = [q for q in QUESTION_BANK if q["category"] in related_cats    and q["text"] not in exclude]

    picked = random.sample(same_pool,    min(2, len(same_pool)))
    picked += random.sample(related_pool, min(n - len(picked), len(related_pool)))

    # 부족하면 전체에서 채움
    if len(picked) < n:
        rest = [q for q in QUESTION_BANK if q["text"] not in exclude and q not in picked]
        picked += random.sample(rest, min(n - len(picked), len(rest)))

    random.shuffle(picked)
    return picked[:n]


def _pick_random(exclude: set, n: int = 5) -> list:
    pool = [q for q in QUESTION_BANK if q["text"] not in exclude]
    return random.sample(pool, min(n, len(pool)))


def show_chatbot_page(rag_service):
    # ── 헤더 ──────────────────────────────────────────────────────────────────
    st.markdown('<p style="font-size:3rem; text-align:center; margin:0;">🤖</p>', unsafe_allow_html=True)
    st.markdown(
        '<h2 style="text-align:center; color:#FF914D; font-family:\'JejuDoldam\', sans-serif;">김서방 대화방</h2>',
        unsafe_allow_html=True,
    )
    st.caption("궁금한 항목을 눌러보세요. 관련 문서를 찾아 쉽게 설명해 드립니다.")
    st.write("---")

    # ── RAG 문서 초기화 ────────────────────────────────────────────────────────
    if "db_initialized" not in st.session_state:
        st.session_state.db_initialized = False

    if not st.session_state.db_initialized:
        if rag_service.count_documents() == 0:
            with st.spinner("문서를 분석 중입니다. 잠시만 기다려주세요..."):
                saved = ingest_docs(rag_service)
                if saved > 0:
                    st.success(f"✅ {saved}개 문서 페이지를 학습했습니다.")
                else:
                    st.warning("⚠️ docs 폴더에 읽을 수 있는 PDF 문서가 없습니다.")
        st.session_state.db_initialized = True

    # ── 세션 상태 초기화 ───────────────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "어서오세요, 저는 김서방입니다요~ 🌾\n축산 분뇨 처리 보조금이나 시설 관련해서 궁금하신 거 있으면 뭐든 물어보세요!"}
        ]
    if "suggested_questions" not in st.session_state:
        st.session_state.suggested_questions = _pick_random(set())
    if "asked_questions" not in st.session_state:
        st.session_state.asked_questions = set()
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None

    # ── 대화 내역 출력 ─────────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # ── 버튼 클릭 → 답변 처리 ─────────────────────────────────────────────────
    if st.session_state.pending_question:
        q = st.session_state.pending_question
        st.session_state.pending_question = None

        with st.chat_message("user"):
            st.write(q["text"])
        st.session_state.messages.append({"role": "user", "content": q["text"]})

        with st.chat_message("assistant"):
            with st.spinner("관련 문서를 찾고 있습니다..."):
                try:
                    response = rag_service.ask(q["text"])
                except Exception as e:
                    response = f"죄송합니다. 오류가 발생했습니다: {e}"
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # 관련 질문으로 버튼 업데이트
        st.session_state.asked_questions.add(q["text"])
        st.session_state.suggested_questions = _pick_related(
            q["category"], st.session_state.asked_questions
        )
        st.rerun()

    # ── 질문 버튼 영역 ─────────────────────────────────────────────────────────
    st.markdown(
        "<p style='color:#888; font-size:0.9rem; margin-top:1.5rem; margin-bottom:0.5rem;'>"
        "💬 <b>궁금한 것을 눌러보세요</b></p>",
        unsafe_allow_html=True,
    )

    for i, q in enumerate(st.session_state.suggested_questions):
        emoji = CATEGORY_EMOJI.get(q["category"], "❓")
        if st.button(f"{emoji} {q['text']}", key=f"qbtn_{i}", use_container_width=True):
            st.session_state.pending_question = q
            st.rerun()

    st.markdown("<div style='margin:0.5rem 0;'></div>", unsafe_allow_html=True)

    # ── 다른 질문 보기 버튼 ────────────────────────────────────────────────────
    if st.button("🔀 다른 질문 보기", key="shuffle_btn", use_container_width=False):
        st.session_state.suggested_questions = _pick_random(st.session_state.asked_questions)
        st.rerun()
