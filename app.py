import streamlit as st
import pandas as pd
import base64
from chatbot_page import show_chatbot_page
from dryer_matching_page import show_dryer_matching_page
import streamlit.components.v1 as components
from modules.region_data_loader import load_region_code
from modules.calculator import diagnose_with_capacity, diagnose_without_capacity
from modules.rag_service import RagService
from ingest import ingest_docs
from modules.openai_service import explain_for_elderly

def get_font_base64(font_path):
    with open(font_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

FILE_PATH = 'data/region_code.csv'
region_map = load_region_code(FILE_PATH)

st.set_page_config(page_title="SolarSludge", page_icon="☀️", layout="centered")

@st.cache_resource
def load_rag_service():
    return RagService()

rag_service = load_rag_service()

font_title_b64 = get_font_base64("EF_jejudoldam.ttf")
font_body_b64 = get_font_base64("text2.ttf")

# CSS 및 폰트 설정
st.markdown(f"""
    <style>
    @font-face {{
        font-family: 'JejuDoldam';
        src: url(data:font/ttf;base64,{font_title_b64}) format('truetype');
    }}
    
    @font-face {{
        font-family: 'CustomBody';
        src: url(data:font/ttf;base64,{font_body_b64}) format('truetype');
    }}

    .stApp {{ background-color: #FDFBF5; }}

    .block-container {{
         max-width: 1000px !important;
         padding-top: 2rem !important;
         padding-bottom: 2rem !important;
    }}

    .stMarkdown, .stSubheader, label, p, h1, h2, h3 {{
        color: #222222 !important; 
    }}

    /* 컨테이너 스타일: 배경 투명, 테두리 아주 연하게 */
    div[data-testid="stVerticalBlockBorderControl"] {{
        background-color: transparent !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        padding: 20px !important;
        border-radius: 12px !important;
    }}

    /* 지역 선택 영역 중앙 정렬 */
    div[data-testid="stVerticalBlockBorderControl"] div.stColumn {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }}

    /* 셀렉트박스 너비 조정 및 중앙 정렬 */
    div[data-testid="stVerticalBlockBorderControl"] div.stSelectbox {{
        width: 80% !important;
        margin: 0 auto !important;
    }}

    /* 질문 라벨 폰트 크기 키우기 */

    label p {{
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }}

    div[data-testid="stVerticalBlock"] > div {{
        margin-bottom: 1rem !important;
    }}

    .stSubheader {{
        margin-top: 0rem !important;  
        margin-bottom: 0.5rem !important;
    }}
    
    div.element-container:first-child .stSubheader {{
        margin-top: 0rem !important;
    }}

    div.stColumns {{
        margin-bottom: 2rem !important; 
    }}

    div.row-widget.stRadio {{
        margin-bottom: 0rem !important;
    }}

    div.element-container:has(.stTextInput), div.element-container:has(.stInfo) {{
        margin-bottom: 0.5rem !important;
    }}

    .stButton>button {{
        width: 100% !important;
        border-radius: 12px !important;
        height: 3.5em !important;
        background-color: transparent !important;
        color: #FF914D !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: 2px solid #FF914D !important;
        transition: all 0.2s ease-in-out !important;
        cursor: pointer !important;
    }}

    .stButton>button:hover {{
        background-color: #FF914D !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(255, 145, 77, 0.2) !important;
    }}

    .stButton>button:active {{
        transform: translateY(0px) !important;
    }}


    /* 테이블 스타일 수정: 크기 축소 및 가운데 정렬 */
    [data-testid="stTable"] {{
        font-size: 0.9rem !important;
    }}
    [data-testid="stTable"] table {{
        width: 80% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }}
    [data-testid="stTable"] th, [data-testid="stTable"] td {{
        text-align: center !important;
        vertical-align: middle !important;
        padding: 4px 8px !important;
    }}
    </style>

""", unsafe_allow_html=True)


if "current_page" not in st.session_state:
    st.session_state.current_page = "analyzer"

with st.sidebar:
    
    st.markdown("### 📊 메뉴 선택")
    if st.button("📊 경제성 분석기 바로가기", use_container_width=True):
        st.session_state.current_page = "analyzer"
         
    st.markdown("---")
    st.markdown("### 🤖 AI 비서에게 물어보기")

    if st.button("💬 해말금 AI 비서 호출", use_container_width=True):
        st.session_state.current_page = "chatbot"
         
    st.image("farmers.png", use_container_width=True)


if st.session_state.current_page == "analyzer":
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None
    if "user_inputs" not in st.session_state:
        st.session_state.user_inputs = {
            "sido": list(region_map.keys())[0],
            "sigun": list(region_map[list(region_map.keys())[0]].keys())[0],
            "pigs": "",
            "know_solar": "알고 있어요",
            "solar": "",
            "know_waste": "알고 있어요",
            "waste": ""
        }

    try:
        with open("sun.png", "rb") as image_file:
            encoded_sun = base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        encoded_sun = ""

    st.html(
        f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; margin-top: -30px; margin-bottom: 0rem; padding-top: 0px;">
            <img src="data:image/png;base64,{encoded_sun}" style="width: 200px; height: auto; display: block; margin: 0 auto; padding: 0; border: none;">
            
            <h1 style="font-family: 'JejuDoldam', sans-serif !important; font-size: 4.5rem; color: #FF914D !important; margin-top: -40px; margin-bottom: 5px; padding-top: 0px; width: 100%; font-weight: bold; line-height: 0.8;">
                해말금
            </h1>
            
            <p style="font-family: 'CustomBody', sans-serif !important; font-size: 1.4rem; color: #555555; margin-top: 5px; margin-bottom: 1rem; font-weight: 500; width: 100%;">
                폐수 처리 경제성 및 태양광 효율 분석 시스템
            </p>
        </div>
        """
    )
    st.write("---")

    st.markdown("### 📌 지역 선택")
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            sido_opts = list(region_map.keys())
            sido_idx = sido_opts.index(st.session_state.user_inputs["sido"]) if st.session_state.user_inputs["sido"] in sido_opts else 0
            selected_sido = st.selectbox("도를 선택하세요", sido_opts, index=sido_idx)
            st.session_state.user_inputs["sido"] = selected_sido
        with col2:
            sigun_opts = list(region_map[selected_sido].keys())
            sigun_idx = sigun_opts.index(st.session_state.user_inputs["sigun"]) if st.session_state.user_inputs["sigun"] in sigun_opts else 0
            selected_sigun = st.selectbox("지역을 선택하세요", sigun_opts, index=sigun_idx)
            st.session_state.user_inputs["sigun"] = selected_sigun
    
    final_code = region_map[selected_sido][selected_sigun]

    st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

    # 1. 돼지 두수 질문
    st.markdown("#### 🐷 현재 사육 중인 돼지 두수는 몇 마리인가요?")
    pigs_raw = st.text_input("현재 사육 중인 돼지 두수는 몇 마리인가요?", value=st.session_state.user_inputs["pigs"], placeholder="숫자만 입력 (예: 2000)", label_visibility="collapsed")
    st.session_state.user_inputs["pigs"] = pigs_raw
    pigs = int(pigs_raw) if pigs_raw.isdigit() else 0

    st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

    # 2. 태양광 질문
    st.markdown("#### ☀️ 태양광 패널 용량을 알고 계신가요?")
    with st.container(border=True):
        solar_radio_opts = ["알고 있어요", "잘 모르겠어요"]
        solar_radio_idx = solar_radio_opts.index(st.session_state.user_inputs["know_solar"]) if st.session_state.user_inputs["know_solar"] in solar_radio_opts else 0
        know_solar = st.radio("태양광 패널 용량을 알고 계신가요?", solar_radio_opts, index=solar_radio_idx, label_visibility="collapsed")
        st.session_state.user_inputs["know_solar"] = know_solar

        if know_solar == "알고 있어요":
             st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
             solar_raw = st.text_input("설치된 태양광 패널 용량 (kW)", value=st.session_state.user_inputs["solar"], placeholder="숫자만 입력 (예: 500)")
             st.session_state.user_inputs["solar"] = solar_raw
             solar_size = int(solar_raw) if (solar_raw and solar_raw.isdigit()) else 0
        else:  
             st.info("💡 용량을 모르시는 경우, 분석 시 50/100/300kW 기준으로 결과를 보여드립니다.")
             solar_size = -1

    st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

    # 3. 분뇨 처리 비용 질문
    st.markdown("#### 💩 한 달 분뇨 처리 비용을 알고 계신가요?")
    with st.container(border=True):
        waste_radio_opts = ["알고 있어요", "잘 모르겠어요"]
        waste_radio_idx = waste_radio_opts.index(st.session_state.user_inputs["know_waste"]) if st.session_state.user_inputs["know_waste"] in waste_radio_opts else 0
        know_waste_cost = st.radio("한 달 분뇨 처리 비용을 알고 계신가요?", waste_radio_opts, index=waste_radio_idx, label_visibility="collapsed")
        st.session_state.user_inputs["know_waste"] = know_waste_cost

        if know_waste_cost == "알고 있어요":
             waste_raw = st.text_input("한 달 분뇨 처리 비용 (만원 단위)", value=st.session_state.user_inputs["waste"], placeholder="숫자만 입력 (예: 120)")
             st.session_state.user_inputs["waste"] = waste_raw
             waste_cost = int(waste_raw) if (waste_raw and waste_raw.isdigit()) else 0
        else:
             st.info("💡 비용을 모르시는 경우, 사육 두수 기반의 평균 비용으로 계산해 드립니다.")
             waste_cost = -1

    st.write("---")
    predict_button = st.button("분석 시작하기")

    if predict_button:
        if pigs > 0:
             treatment_cost_input = waste_cost * 10000 if waste_cost > 0 else None
             try:
                 if know_solar == "알고 있어요":
                     raw_res = diagnose_with_capacity(
                         region_code=final_code, head_count=float(pigs),
                         solar_capacity_kw=float(solar_size), monthly_treatment_cost=treatment_cost_input
                     )
                     st.session_state.analysis_results = {float(solar_size): raw_res}
                 else:
                     st.session_state.analysis_results = diagnose_without_capacity(
                         region_code=final_code, head_count=float(pigs),
                         monthly_treatment_cost=treatment_cost_input
                     )
                 
                 # [핵심 수정] 계산이 끝나면 화면을 강제로 새로고침해서 최신 회수기간 데이터를 반영함
                 st.rerun()

             except ValueError as e:
                 st.error(f"❌ 분석 불가: {e}")
        else:
             st.warning("⚠️ 돼지 사육 두수를 입력해 주세요.")

    if st.session_state.analysis_results:
        st.subheader("분석 결과")
        target_capacities = sorted(st.session_state.analysis_results.keys())
        tabs = st.tabs([f"{int(c)}kW 설치 시" for c in target_capacities])

        for i, tab in enumerate(tabs):
            cap = target_capacities[i]
            scenario_data = st.session_state.analysis_results[cap]
            with tab:
                # 테이블 데이터 구성
                metrics = {
                    "구분": ["월 절감액", "예상 처리비", "절감률", "회수기간"],
                    "보수": [
                        f"{int(scenario_data['보수']['monthly_saving']):,}원",
                        f"{int(scenario_data['보수']['new_cost']):,}원",
                        f"{scenario_data['보수']['saving_rate_pct']}%",
                        f"{scenario_data['보수']['roi_months'] if scenario_data['보수']['roi_months'] else '-'}개월"
                    ],
                    "기준": [
                        f"{int(scenario_data['기준']['monthly_saving']):,}원",
                        f"{int(scenario_data['기준']['new_cost']):,}원",
                        f"{scenario_data['기준']['saving_rate_pct']}%",
                        f"{scenario_data['기준']['roi_months'] if scenario_data['기준']['roi_months'] else '-'}개월"
                    ],
                    "낙관": [
                        f"{int(scenario_data['낙관']['monthly_saving']):,}원",
                        f"{int(scenario_data['낙관']['new_cost']):,}원",
                        f"{scenario_data['낙관']['saving_rate_pct']}%",
                        f"{scenario_data['낙관']['roi_months'] if scenario_data['낙관']['roi_months'] else '-'}개월"
                    ]
                }
                
                df = pd.DataFrame(metrics).set_index("구분")
                st.table(df)

                if st.button(f"쉬운 설명 보기 ({int(cap)}kW)", key=f"explain_{cap}"):
                    with st.spinner("어르신을 위한 설명을 준비 중입니다..."):
                        try:
                            explanation = explain_for_elderly(scenario_data, cap)
                            st.info(explanation)
                        except Exception as e:
                            st.error(f"설명을 생성하는 중 오류가 발생했습니다: {e}")

        st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align:center;color:#888;font-size:0.9rem;margin-bottom:0.5rem;'>"
            "분석 결과를 바탕으로 가까운 건조기·탈수기 업체에 견적을 받아보세요.</p>",
            unsafe_allow_html=True,
        )
        if st.button("🏭 건조기 견적 상담받기", key="go_to_dryer_matching"):
            st.session_state.current_page = "dryer_matching"
            st.rerun()


elif st.session_state.current_page == "chatbot":
    show_chatbot_page(rag_service)

elif st.session_state.current_page == "dryer_matching":
    show_dryer_matching_page(
        st.session_state.get("analysis_results"),
        st.session_state.get("user_inputs", {}),
    )

