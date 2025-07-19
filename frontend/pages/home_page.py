import streamlit as st
import requests
from pages import analyze_page, routine_page, profile_page, compare_page
from utils import logout,API_BASE_URL, get_auth_header, inject_custom_css


def render():
    inject_custom_css()

    st.markdown("""
    <div class="brand-container">
        <h1 class="brand-title">SKINSAGE</h1>
        <div class="header-underline"></div>
        <p class="brand-tagline">Your Personalized Skincare Analysis Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    # Logout button (right-aligned using a row or just use columns for alignment)
    logout_col1, logout_col2 = st.columns([6, 1])
    with logout_col2:
        if st.button("Logout", key="top_logout", use_container_width=True):
            logout()




    # Sidebar navigation
    with st.sidebar:
        st.subheader("Navigation")
        st.markdown('<h2 style="color: var(--sage-dark);">Navigation</h2>', unsafe_allow_html=True)
        nav_options = {
            "🔍 Analyze Product": "analyze",
            "✨ Your Routine": "routine",
            "👤 Profile": "profile", 
            "🔄 Compare Products": "compare"
        }
        selection = st.radio("Go to", list(nav_options.keys()),key="nav_radio")
        page = nav_options[selection]

    # User profile header
    try:
        response = requests.get(
            f"{API_BASE_URL}/profile",
            headers=get_auth_header()
        )
        if response.status_code == 200:
            profile = response.json()
            st.caption(f"👤 {profile.get('email', '')} | 🧴 {profile.get('skin_type', '').capitalize()} skin | ⚠️ {', '.join([c.capitalize() for c in profile.get('concerns', [])] or 'No concerns')}")
    except:
        pass
    
    st.markdown("---")
    
    # Page routing
    if page == "analyze":
        analyze_page.render()
    elif page == "routine":
        routine_page.render()
    elif page == "profile":
        profile_page.render()
    elif page == "compare":
        compare_page.render()