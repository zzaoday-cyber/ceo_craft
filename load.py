import streamlit as st

st.set_page_config(page_title="CEO Craft - 시작", layout="wide")

st.title("CEO Craft")
st.subheader("회사 이름을 입력하세요")

company_name = st.text_input("회사 이름", placeholder="예: 미래제조")

if st.button("시작하기", type="primary"):
    name = company_name.strip()
    if not name:
        st.error("회사 이름을 입력해주세요.")
    else:
        st.session_state["company_name"] = name
        st.switch_page("main.py")
