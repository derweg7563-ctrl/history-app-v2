import streamlit as st
import time

# 👇 1. AI 보조교사 모듈 불러오기
import ai_teacher

# 💡 구글 생성형 AI 패키지 불러오기
try:
    import google.generativeai as genai
except ImportError:
    st.error("🚨 `google-generativeai` 패키지가 필요합니다.")

def show_page():
    st.title("🕵️‍♂️ AI 유물 탐정이 되어보기")
    st.subheader("💬[1단계] 가상현실 박물관을 탐험하고, 진짜 AI 탐정에게 비밀을 물어보세요!")

    # ---------------------------------------------------------
    # 🏛️ 1단계: 구글 아트앤컬쳐 관찰 영역 (상단)
    # ---------------------------------------------------------
    st.markdown("""
        <style>
        .gac-card {
            background: linear-gradient(135deg, #2E7D32, #81C784);
            border-radius: 20px; padding: 30px; text-align: center; color: white;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15); margin: 20px 0;
        }
        .gac-card h3 { color: white !important; font-weight: 900; margin-bottom: 15px; }
        .gac-card p { font-size: 1.1rem; color: #E8F5E9; margin-bottom: 25px; font-weight: bold; line-height: 1.5; }
        .gac-btn {
            background-color: #ffffff; color: #2E7D32 !important; padding: 15px 40px;
            border-radius: 50px; font-weight: 900; font-size: 1.2rem; text-decoration: none; display: inline-block;
            transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .gac-btn:hover { transform: translateY(-3px); box-shadow: 0 6px 15px rgba(0,0,0,0.2); color: #1B5E20 !important; }
        </style>
        
        <div class="gac-card">
            <h3>🏛️ 국립민속박물관 가상현실(VR) 탐험</h3>
            <p>먼저 박물관에 입장해서 옛날 사람들의 물건을 요리조리 관찰해 보세요.<br>가장 신기하고 궁금한 물건의 이름을 꼭 기억해 두세요!</p>
            <a href="https://artsandculture.google.com/partner/national-folk-museum-of-korea?hl=ko" target="_blank" class="gac-btn">
                🚪 국립민속박물관 입장하기 (새 창 열림)
            </a>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🧠 구글 Gemini AI 설정 영역 (자동 탐색 마법)
    # ---------------------------------------------------------
    try:
        genai.configure(api_key=st.secrets["google"]["api_key"])
    except Exception as e:
        st.error("🚨 secrets.toml 파일에 구글 열쇠가 없습니다!")

    if "gemini_chat" not in st.session_state:
        try:
            valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if not valid_models:
                st.error("🚨 앗! 이 API 키로는 쓸 수 있는 AI 모델이 없습니다.")
                st.stop()
            
            auto_model_name = valid_models[0]
            model = genai.GenerativeModel(auto_model_name)
            st.session_state.gemini_chat = model.start_chat(history=[])
            
        except Exception as e:
            st.error(f"🚨 구글 서버 접속 에러: {e}")
            st.stop()

    # ---------------------------------------------------------
    # 🕵️‍♂️ 2단계: AI 탐정 채팅 영역 (하단)
    # ---------------------------------------------------------
    st.markdown("### 💬 [2단계] 똑똑해진 AI 유물 탐정에게 질문하기")
    st.info("💡 박물관에서 본 아무 유물이나 다 물어보세요! 구글의 지식으로 무장한 AI 탐정이 친절하게 알려줍니다.")

    # 🎯 [핵심 1] 대화 내용이 너무 길어지지 않게 스크롤 박스(height=400) 안에 가둡니다!
    chat_box = st.container(height=400)
    
    with chat_box:
        if "messages_2_2" not in st.session_state:
            st.session_state.messages_2_2 = [
                {"role": "assistant", "content": "안녕하세요! 저는 구글의 인공지능 두뇌를 가진 '진짜' AI 유물 탐정입니다. 🕵️‍♂️ 국립민속박물관에서 어떤 신기한 물건을 보셨나요? 무엇이든 물어보시면 다 대답해 드릴게요!"}
            ]

        for msg in st.session_state.messages_2_2:
            avatar = "🕵️‍♂️" if msg["role"] == "assistant" else "👩‍🎓"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # 🎯 [핵심 2] 맨 밑으로 도망가는 chat_input 대신, 그 자리에 고정되는 일반 폼(Form)을 사용합니다!
    with st.form("chat_form_2_2", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("질문 입력", label_visibility="collapsed", placeholder="아무 유물이나 물어보세요! (예: 떡살이 뭐야?)")
        with col2:
            submit_btn = st.form_submit_button("질문하기 🚀", use_container_width=True)

    if submit_btn and user_input:
        st.session_state.messages_2_2.append({"role": "user", "content": user_input})
        
        with chat_box:
            with st.chat_message("user", avatar="👩‍🎓"):
                st.markdown(user_input)
            
            with st.chat_message("assistant", avatar="🕵️‍♂️"):
                message_placeholder = st.empty()
                prompt = f"너는 초등학생들에게 우리나라 전통 유물과 역사를 친절하게 설명해주는 'AI 유물 탐정'이야. 다음 학생의 질문에 초등학생이 이해하기 쉽게, 이모지를 섞어서 친절하고 재미있게 3~4문장으로 대답해줘. 질문: {user_input}"
                
                try:
                    response = st.session_state.gemini_chat.send_message(prompt, stream=True)
                    full_response = ""
                    for chunk in response:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                        time.sleep(0.05) 
                    message_placeholder.markdown(full_response)
                    st.session_state.messages_2_2.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    error_msg = f"앗, 구글 AI 탐정이 대답을 찾는 데 문제가 생겼어요. (오류: {e})"
                    message_placeholder.markdown(error_msg)
                    st.session_state.messages_2_2.append({"role": "assistant", "content": error_msg})
        
        # 입력 후 화면을 깔끔하게 유지하기 위해 새로고침
        st.rerun()

    # ---------------------------------------------------------
    # 🤖 3. AI 보조교사 호출 (맨 아래)
    # ---------------------------------------------------------
    activity_desc = "이 화면은 VR 박물관을 탐험하고, AI 유물 탐정 챗봇에게 전통 유물에 대해 질문하는 곳입니다."
    ai_teacher.show_ai_teacher(activity_name="활동 2-2. AI 유물 탐정이 되어보기", context_description=activity_desc)