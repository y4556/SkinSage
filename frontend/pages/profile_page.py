import streamlit as st
import requests
from utils import get_auth_header, logout,API_BASE_URL

def render():
    st.title("👤 Your Profile")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/profile",
            headers=get_auth_header()
        )
        
        if response.status_code == 200:
            profile = response.json()
            
            col1, col2 = st.columns([1, 3])
            with col1:
                initials = ''.join([n[0] for n in profile.get("email", "").split("@")[0].split(".")])
                st.markdown(
                    f"""
                    <div class="profile-avatar">
                        {initials.upper()}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                #     f"""
                #     <div style="
                #         background: linear-gradient(45deg, #6a5acd, #ff7eb9);
                #         width: 120px;
                #         height: 120px;
                #         border-radius: 50%;
                #         display: flex;
                #         align-items: center;
                #         justify-content: center;
                #         font-size: 48px;
                #         color: white;
                #         margin: 0 auto;
                #     ">{initials.upper()}</div>
                #     """,
                #     unsafe_allow_html=True
                # )
            
            with col2:
                st.subheader("Email")
                st.code(profile.get("email", ""), language="text")
                
                st.subheader("Skin Type")
                st.info(profile.get("skin_type", "").capitalize())
                
                st.subheader("Skin Concerns")
                concerns = [c.capitalize() for c in profile.get("concerns", [])]
                if concerns:
                    st.info(", ".join(concerns))
                else:
                    st.info("None specified")
        else:
            st.error("Failed to load profile data")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        
    if st.button("Logout", use_container_width=True, key="profile_logout"):
        logout()
