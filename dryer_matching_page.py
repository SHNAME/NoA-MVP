import streamlit as st
import streamlit.components.v1 as components
import math

# ── 시도별 대략 좌표 ──────────────────────────────────────────────────────────
SIDO_COORDS = {
    "서울특별시":      (37.5665, 126.9780),
    "부산광역시":      (35.1796, 129.0756),
    "대구광역시":      (35.8714, 128.6014),
    "인천광역시":      (37.4563, 126.7052),
    "광주광역시":      (35.1595, 126.8526),
    "대전광역시":      (36.3504, 127.3845),
    "울산광역시":      (35.5384, 129.3114),
    "세종특별자치시":  (36.4800, 127.2890),
    "경기도":          (37.4138, 127.5183),
    "강원도":          (37.8228, 128.1555),
    "강원특별자치도":  (37.8228, 128.1555),
    "충청북도":        (36.6357, 127.4912),
    "충청남도":        (36.5184, 126.8000),
    "전라북도":        (35.7175, 127.1530),
    "전북특별자치도":  (35.7175, 127.1530),
    "전라남도":        (34.8679, 126.9910),
    "경상북도":        (36.4919, 128.8889),
    "경상남도":        (35.4606, 128.2132),
    "제주특별자치도":  (33.4996, 126.5312),
}

# ── 목업 업체 데이터 ──────────────────────────────────────────────────────────
MOCK_COMPANIES = [
    {
        "id": 1,
        "name": "한국환경기계(주)",
        "location": "충청남도 당진시",
        "coords": (36.8926, 126.6458),
        "specialty": ["건조기", "탈수기"],
        "description": "농업 분뇨 전문 건조·탈수 설비 제조 20년 이상 경력. 전국 200여 농장 납품 실적. 현장 맞춤 설계 무료 제공.",
        "phone": "041-XXX-XXXX",
        "rating": 4.7,
        "review_count": 38,
        "lead_time": "6~8주",
        "price_range": "3,000~8,000만원",
    },
    {
        "id": 2,
        "name": "농업환경시스템(주)",
        "location": "전라북도 익산시",
        "coords": (35.9483, 126.9577),
        "specialty": ["건조기"],
        "description": "스크류 프레스 탈수 방식 특허 보유. 에너지 효율 최적화 건조기 개발 전문. 소비 전력 업계 최저 수준.",
        "phone": "063-XXX-XXXX",
        "rating": 4.5,
        "review_count": 24,
        "lead_time": "8~10주",
        "price_range": "2,500~6,000만원",
    },
    {
        "id": 3,
        "name": "(주)에코드라이텍",
        "location": "경상북도 상주시",
        "coords": (36.3986, 128.1587),
        "specialty": ["건조기", "탈수기"],
        "description": "저온 건조 방식으로 에너지 절감 최대화. 태양광 연계 건조 시스템 시공 가능. IoT 원격 모니터링 기본 포함.",
        "phone": "054-XXX-XXXX",
        "rating": 4.8,
        "review_count": 51,
        "lead_time": "4~6주",
        "price_range": "4,000~9,000만원",
    },
    {
        "id": 4,
        "name": "그린텍환경기계",
        "location": "경기도 화성시",
        "coords": (37.1996, 126.8312),
        "specialty": ["탈수기"],
        "description": "소규모 농장 특화 소형 탈수 설비 전문. 설치 및 AS 전국 당일 대응 체계 구축.",
        "phone": "031-XXX-XXXX",
        "rating": 4.3,
        "review_count": 17,
        "lead_time": "3~4주",
        "price_range": "1,500~4,000만원",
    },
    {
        "id": 5,
        "name": "(주)바이오마스텍",
        "location": "충청북도 청주시",
        "coords": (36.6424, 127.4890),
        "specialty": ["건조기", "탈수기"],
        "description": "25년 업력 국내 1세대 분뇨처리 기계 전문 업체. 대형 양돈장 납품 다수. 퇴비화 연계 솔루션 제공.",
        "phone": "043-XXX-XXXX",
        "rating": 4.6,
        "review_count": 63,
        "lead_time": "6~10주",
        "price_range": "5,000~1억2,000만원",
    },
    {
        "id": 6,
        "name": "진흥환경기계(주)",
        "location": "전라남도 나주시",
        "coords": (35.0160, 126.7108),
        "specialty": ["건조기"],
        "description": "열풍 건조 방식 자체 개발. 분뇨 비료화(퇴비화) 연계 건조 솔루션 제공. 남부 지역 최다 설치 실적.",
        "phone": "061-XXX-XXXX",
        "rating": 4.4,
        "review_count": 29,
        "lead_time": "5~7주",
        "price_range": "2,000~5,500만원",
    },
    {
        "id": 7,
        "name": "경남환경설비(주)",
        "location": "경상남도 함안군",
        "coords": (35.2726, 128.4073),
        "specialty": ["탈수기", "건조기"],
        "description": "경남 지역 최다 설치 실적. 현장 맞춤형 설계 및 AS 1년 보증. 설치 후 3개월 무상 점검.",
        "phone": "055-XXX-XXXX",
        "rating": 4.5,
        "review_count": 44,
        "lead_time": "5~8주",
        "price_range": "3,500~8,500만원",
    },
    {
        "id": 8,
        "name": "(주)해성드라이시스",
        "location": "강원도 원주시",
        "coords": (37.3422, 127.9202),
        "specialty": ["건조기"],
        "description": "최신 IoT 원격 모니터링 탑재 스마트 건조기. 전력 자동 제어로 운영비 절감. 스마트팜 연동 가능.",
        "phone": "033-XXX-XXXX",
        "rating": 4.2,
        "review_count": 11,
        "lead_time": "6~8주",
        "price_range": "4,500~1억원",
    },
]


def _haversine(lat1, lon1, lat2, lon2) -> float:
    """두 좌표 간 직선 거리 반환 (km)"""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi   = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return round(2 * R * math.asin(math.sqrt(a)), 1)


def _star_html(rating: float) -> str:
    full  = int(rating)
    half  = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + "☆" * half + "☆" * empty


def _render_company_card(rank: int, company: dict, analysis_results, user_inputs):
    """업체 카드 1개 렌더링"""
    cid = company["id"]
    sent_key = f"quote_sent_{cid}"
    if sent_key not in st.session_state:
        st.session_state[sent_key] = False

    specialty_badges = " ".join(
        f'<span style="background:#FFF0E6;color:#FF914D;border:1px solid #FF914D;'
        f'border-radius:20px;padding:2px 10px;font-size:0.78rem;font-weight:600;">{s}</span>'
        for s in company["specialty"]
    )

    dist_color = "#27ae60" if company["distance"] < 100 else ("#e67e22" if company["distance"] < 200 else "#c0392b")

    with st.container(border=True):
        # ── 상단: 순위 / 업체명 / 전문분야 / 거리 ──
        col_info, col_dist = st.columns([3, 1])
        with col_info:
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:10px;flex-wrap:wrap;'>"
                f"  <span style='background:#FF914D;color:white;border-radius:50%;width:28px;height:28px;"
                f"    display:inline-flex;align-items:center;justify-content:center;"
                f"    font-weight:700;font-size:0.85rem;flex-shrink:0;'>{rank}</span>"
                f"  <span style='font-size:1.15rem;font-weight:700;color:#222;'>{company['name']}</span>"
                f"  {specialty_badges}"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='margin:4px 0 0 38px;color:#666;font-size:0.9rem;'>📍 {company['location']}</p>",
                unsafe_allow_html=True,
            )
        with col_dist:
            st.markdown(
                f"<div style='text-align:right;'>"
                f"  <span style='font-size:1.4rem;font-weight:700;color:{dist_color};'>{company['distance']} km</span><br>"
                f"  <span style='font-size:0.75rem;color:#999;'>직선 거리</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin:4px 0;'></div>", unsafe_allow_html=True)

        # ── 중단: 별점 / 설명 ──
        rating_html = _star_html(company["rating"])
        st.markdown(
            f"<span style='color:#f1c40f;font-size:1rem;'>{rating_html}</span> "
            f"<span style='color:#555;font-size:0.88rem;'>{company['rating']} ({company['review_count']}건)</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='color:#444;font-size:0.92rem;margin:6px 0;'>{company['description']}</p>",
            unsafe_allow_html=True,
        )

        # ── 하단: 세부 정보 ──
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"📞 **{company['phone']}**")
        with c2:
            st.markdown(f"⏱ 납기 **{company['lead_time']}**")
        with c3:
            st.markdown(f"💰 **{company['price_range']}**")

        st.markdown("<div style='margin:4px 0;'></div>", unsafe_allow_html=True)

        # ── 견적 요청 버튼 ──
        if st.session_state[sent_key]:
            st.success("✅ 견적 요청이 완료되었습니다! 업체에서 영업일 1~2일 내 연락드릴 예정입니다.")
            with st.expander("📋 전달된 분석 결과 확인하기"):
                _render_analysis_summary(analysis_results, user_inputs)
        else:
            if st.button(f"📩 견적 요청하기", key=f"quote_btn_{cid}"):
                st.session_state[sent_key] = True
                st.rerun()


def _render_analysis_summary(analysis_results, user_inputs):
    """견적 요청 시 함께 전달되는 분석 결과 요약"""
    import pandas as pd

    sido = user_inputs.get("sido", "")
    sigun = user_inputs.get("sigun", "")
    pigs = user_inputs.get("pigs", "")

    st.markdown(
        f"**농장 정보:** {sido} {sigun} | 사육 두수 {pigs}마리",
        unsafe_allow_html=False,
    )
    st.markdown("---")

    if not analysis_results:
        st.warning("분석 결과가 없습니다.")
        return

    target_capacities = sorted(analysis_results.keys())
    tabs = st.tabs([f"{int(c)}kW" for c in target_capacities])

    for i, tab in enumerate(tabs):
        cap = target_capacities[i]
        scenario_data = analysis_results[cap]
        with tab:
            metrics = {
                "구분": ["월 절감액", "예상 처리비", "절감률", "회수기간"],
                "보수": [
                    f"{int(scenario_data['보수']['monthly_saving']):,}원",
                    f"{int(scenario_data['보수']['new_cost']):,}원",
                    f"{scenario_data['보수']['saving_rate_pct']}%",
                    f"{scenario_data['보수']['roi_months'] or '-'}개월",
                ],
                "기준": [
                    f"{int(scenario_data['기준']['monthly_saving']):,}원",
                    f"{int(scenario_data['기준']['new_cost']):,}원",
                    f"{scenario_data['기준']['saving_rate_pct']}%",
                    f"{scenario_data['기준']['roi_months'] or '-'}개월",
                ],
                "낙관": [
                    f"{int(scenario_data['낙관']['monthly_saving']):,}원",
                    f"{int(scenario_data['낙관']['new_cost']):,}원",
                    f"{scenario_data['낙관']['saving_rate_pct']}%",
                    f"{scenario_data['낙관']['roi_months'] or '-'}개월",
                ],
            }
            df = pd.DataFrame(metrics).set_index("구분")
            st.table(df)


def show_dryer_matching_page(analysis_results, user_inputs):
    """건조기·탈수기 업체 매칭 메인 페이지"""

    # ── 페이지 진입 시 최상단 스크롤 ──
    components.html(
        "<script>window.parent.document.querySelector('.main').scrollTo(0, 0);</script>",
        height=0,
    )

    # ── 헤더 ──
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:1.2rem;">
            <h2 style="color:#FF914D; margin-bottom:0.3rem;">🏭 건조기 · 탈수기 업체 매칭</h2>
            <p style="color:#555; font-size:1rem;">
                선택하신 지역과 가까운 순으로 정렬되었습니다.<br>
                <strong>견적 요청 시 분석 결과가 업체에 자동 전달됩니다.</strong>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── 사용자 지역 ──
    sido  = user_inputs.get("sido", "")
    sigun = user_inputs.get("sigun", "")
    user_lat, user_lon = SIDO_COORDS.get(sido, (36.5, 127.5))

    st.info(f"📍 기준 지역: **{sido} {sigun}**")

    # ── 거리 계산 및 정렬 ──
    companies_with_dist = sorted(
        [{**c, "distance": _haversine(user_lat, user_lon, c["coords"][0], c["coords"][1])}
         for c in MOCK_COMPANIES],
        key=lambda x: x["distance"],
    )

    st.markdown("---")

    for rank, company in enumerate(companies_with_dist, 1):
        _render_company_card(rank, company, analysis_results, user_inputs)
        st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("← 분석 결과로 돌아가기", key="back_to_analyzer"):
        st.session_state.current_page = "analyzer"
        st.rerun()
