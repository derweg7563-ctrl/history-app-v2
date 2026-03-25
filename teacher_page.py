import streamlit as st
from pymongo import MongoClient
import stu_dash

@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

try:
    client = init_connection()
    db = client["school_project"]
    users_collection = db["users"]
    db_connected = True
except Exception as e:
    db_connected = False
    st.error(f"🚨 DB 연결 에러: {e}")

def show_page(*args, **kwargs):
    st.title("👩‍🏫 선생님 전용 관리 대시보드")
    st.info("우리 반 학생들의 가입 현황을 관리하고, 학생들의 학습 진행도를 한눈에 확인하는 공간입니다.")
    
    if not db_connected:
        st.warning("데이터베이스에 연결할 수 없습니다.")
        return

    students = list(users_collection.find({"role": "학생"}))

    st.markdown("### 👥 가입한 학생 명단 및 관리")
    
    if len(students) == 0:
        st.write("아직 가입한 학생이 없습니다.")
    else:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1: st.markdown("**순번**")
        with col2: st.markdown("**학생 아이디 (이름)**")
        with col3: st.markdown("**관리**")
        st.markdown("---")

        for idx, student in enumerate(students):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1: st.write(idx + 1)
            with c2: st.write(f"**{student['username']}**")
            with c3:
                if st.button("🗑️ 삭제", key=f"del_{student['username']}", help="이 학생의 계정을 삭제합니다."):
                    users_collection.delete_one({"username": student["username"]})
                    st.success(f"'{student['username']}' 학생 계정이 삭제되었습니다.")
                    st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("### 🎓 학생별 탐험 일지 (대시보드) 확인")
    st.write("아래 학생의 이름을 클릭하여 해당 학생이 남긴 발자국을 확인해 보세요!")

    if len(students) == 0:
        st.write("확인할 학생 기록이 없습니다.")
    else:
        for student in students:
            target_name = student["username"]
            with st.expander(f"📂 {target_name} 학생의 탐험 일지 열어보기"):
                stu_dash.show_page(target_student=target_name)