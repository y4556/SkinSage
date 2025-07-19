import streamlit as st
from pages import login_page, home_page
from utils import inject_custom_css

def main():
    inject_custom_css()
    
    st.set_page_config(
        page_title="SkinSage - Personalized Skincare Assistant",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if "token" not in st.session_state:
        st.session_state.token = None
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "report" not in st.session_state:
        st.session_state.report = None
    if "auth_page" not in st.session_state:
        st.session_state.auth_page = "login"
    if "analyzed" not in st.session_state:
        st.session_state.analyzed = False
    if "routine_data" not in st.session_state:
        st.session_state.routine_data = None
    if "trending_products" not in st.session_state:
        st.session_state.trending_products = None
    
    # Page routing
    if not st.session_state.token:
        login_page.render()
    else:
        home_page.render()
    
    st.markdown("---")
    st.caption("© 2025 SkinSage | AI-Powered Skincare Analysis")

if __name__ == "__main__":
    main()