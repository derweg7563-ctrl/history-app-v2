import streamlit as st
import datetime
import urllib.parse
from pymongo import MongoClient

# 👇 1. AI 보조교사 모듈 불러오기
import ai_teacher

# 구글 생성형 AI 패키지
try:
    import google.generativeai as genai
except ImportError:
    st.error("🚨 `google-generativeai` 패키지가 필요합니다.")

# DB 연결
@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

try:
    client = init_connection()
    db = client["school_project"]
    collection = db["local_history"] 
    db_connected = True
except Exception as e:
    db_connected = False
    st.error(f"🚨 DB 연결 에러: {e}")

# 🎯 선생님의 원래 구글 키 적용
try:
    genai.configure(api_key=st.secrets["google"]["api_key"])
except Exception as e:
    st.error("🚨 secrets.toml 파일에 구글 열쇠가 없습니다!")

def get_origin_story(keyword):
    try:
        valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        auto_model_name = valid_models[0]
        model = genai.GenerativeModel(auto_model_name)
        
        prompt = f"너는 경기도 '평택시'의 향토 역사를 아주 잘 아는 초등학교 선생님이야. 3학년 학생이 '{keyword}'라는 지명(땅, 산, 강 이름)을 검색했어. 이 이름이 왜 붙여졌는지 그 유래와 한자 뜻을 초등학교 3학년이 이해하기 쉽게 이모지를 섞어서 3~4문장으로 재미있게 설명해줘."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"앗! AI가 잠시 쉬고 있어요. (오류: {e})"

def show_page():
    # 🎨 [추가됨] 대시보드 이동용 둥근 버튼을 위한 CSS 마법!
    st.markdown("""
        <style>
        .dash-praise {
            text-align: center;
            font-size: 1.5rem;
            font-weight: bold;
            color: #2E7D32;
            background-color: #E8F5E9;
            padding: 20px;
            border-radius: 20px;
            border: 3px dashed #81C784;
            margin-top: 40px;
            margin-bottom: 20px;
        }
        /* 동그란 버튼을 만들기 위한 CSS */
        div.element-container:has(.dash-btn-hook) + div.element-container {
            display: flex;
            justify-content: center;
        }
        div.element-container:has(.dash-btn-hook) + div.element-container button {
            width: 160px !important;
            height: 160px !important;
            border-radius: 50% !important; /* 👈 완전 둥근 원형을 만드는 핵심 설정 */
            background: linear-gradient(135deg, #FFD54F, #FFB300) !important;
            color: #4E342E !important;
            font-size: 1.2rem !important;
            font-weight: 900 !important;
            border: 5px solid #FFF8E1 !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15) !important;
            white-space: pre-wrap !important;
            transition: all 0.3s ease !important;
        }
        div.element-container:has(.dash-btn-hook) + div.element-container button:hover {
            transform: scale(1.08) !important; /* 마우스를 올리면 통통 튀어오릅니다 */
            box-shadow: 0 12px 25px rgba(0,0,0,0.25) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏷️ 평택의 땅 이름 비밀 찾기")
    st.info("💡 우리 동네 이름, 산, 강 이름(예: 고덕면, 안성천, 부락산)을 검색하면 이름의 유래를 알려줍니다!")

    current_student = st.session_state.get('username', '학생')

    # AI 검색기
    col_search, col_btn = st.columns([3, 1])
    with col_search:
        search_origin = st.text_input("📍 검색어 입력", key="search_origin")
    with col_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        search_origin_btn = st.button("유래 찾기 🚀")
        
    if search_origin_btn and search_origin:
        with st.spinner('지역 사전을 펼치고 뜻을 풀이하는 중... 📜'):
            result = get_origin_story(search_origin)
            st.success(f"**🤖 AI 역사학자의 답변:**\n\n{result}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("👀 **검색한 장소의 실제 모습이 궁금하다면?**")
            
            encoded_keyword = urllib.parse.quote(search_origin)
            naver_url = f"https://search.naver.com/search.naver?where=image&sm=tab_jum&query={encoded_keyword}"
            st.link_button(f"'{search_origin}' 네이버 이미지 검색하기 🔍", naver_url, use_container_width=True)
            
    st.markdown("---")

    # 기록 폼
    with st.form("name_origin_form", clear_on_submit=True):
        st.write("✍️ **조사한 땅 이름의 뜻을 친구들에게 소개하듯 정리해 보세요.**")
        place_name = st.text_input("📍 장소 이름")
        place_origin = st.text_area("📖 이름에 담긴 뜻과 유래 (나의 생각 포함)", height=150)
        
        if st.form_submit_button("이름의 비밀 백과사전에 저장하기 🚀", use_container_width=True):
            if place_name and place_origin:
                if db_connected:
                    collection.insert_one({"type": "지역명유래", "username": current_student, "place_name": place_name, "origin": place_origin, "timestamp": datetime.datetime.now()})
                    st.success("🎉 땅 이름의 비밀이 기록 완료되었어요!")
                    st.balloons()
            else:
                st.warning("⚠️ 장소 이름과 유래를 모두 적어주세요!")

    # =========================================================
    # 🏅 [추가됨] 칭찬 메시지 & 대시보드로 가는 동그란 버튼!
    # =========================================================
    st.markdown(f'<div class="dash-praise">🎉 지금까지 열심히 공부한 <span style="color:#E65100;">{current_student}</span> 대원을 칭찬해!<br>우리가 얼마나 열심히 했는지 알아볼까? 👀</div>', unsafe_allow_html=True)
    
    st.markdown("<span class='dash-btn-hook'></span>", unsafe_allow_html=True)
    if st.button("📊\n나의 발자국\n확인하기"):
        st.session_state.current_page = "stu_dash"  # 대시보드 페이지로 이동 명령!
        st.rerun()

    # ---------------------------------------------------------
    # 🤖 AI 보조교사 호출 (파일 맨 아래)
    # ---------------------------------------------------------
    activity_desc = "이 화면은 평택의 땅 이름(부락산, 안성천 등)을 검색하여 AI 지역학자에게 유래를 물어보고 백과사전에 기록하는 곳입니다. 모든 활동의 마지막 단계이므로, 학생이 잘 마무리하고 '나의 발자국 확인하기' 버튼을 누르도록 독려해 주세요."
    ai_teacher.show_ai_teacher(activity_name="활동 3-3. 평택의 땅 이름 비밀 찾기", context_description=activity_desc)