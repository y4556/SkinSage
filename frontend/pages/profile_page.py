# import streamlit as st
# import requests
# from utils import get_auth_header, logout,API_BASE_URL

# def render():
#     st.title("👤 Your Profile")
    
#     try:
#         response = requests.get(
#             f"{API_BASE_URL}/profile",
#             headers=get_auth_header()
#         )
        
#         if response.status_code == 200:
#             profile = response.json()
            
#             col1, col2 = st.columns([1, 3])
            
#             with col2:
#                 st.subheader("Email")
#                 st.info(profile.get("email", ""))
                
#                 st.subheader("Skin Type")
#                 st.info(profile.get("skin_type", "").capitalize())
                
#                 st.subheader("Skin Concerns")
#                 concerns = [c.capitalize() for c in profile.get("concerns", [])]
#                 if concerns:
#                     st.info(", ".join(concerns))
#                 else:
#                     st.info("None specified")
#         else:
#             st.error("Failed to load profile data")
#     except Exception as e:
#         st.error(f"Error: {str(e)}")
        
#     if st.button("Logout", use_container_width=True, key="profile_logout"):
#         logout()
import streamlit as st
import requests
from utils import get_auth_header, logout, API_BASE_URL

import streamlit as st
import requests
from utils import get_auth_header, logout, API_BASE_URL

def render():
    st.title("👤 Your Profile")
    
    # Initialize session state for edit mode
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    
    try:
        # Fetch profile data
        response = requests.get(
            f"{API_BASE_URL}/profile",
            headers=get_auth_header()
        )
        
        if response.status_code == 200:
            profile = response.json()
            
            if st.session_state.edit_mode:
                # Edit Mode UI
                with st.form("profile_form", clear_on_submit=False):
                    # Skin Type Selector
                    skin_type_options = ["Normal", "Dry", "Oily", "Combination", "Sensitive"]
                    skin_type_index = skin_type_options.index(
                        profile.get("skin_type", "").capitalize()
                    ) if profile.get("skin_type") and profile["skin_type"].capitalize() in skin_type_options else 0
                    
                    skin_type = st.selectbox(
                        "Skin Type",
                        options=skin_type_options,
                        index=skin_type_index
                    ).lower()
                    
                    # Skin Concerns Selector
                    concerns_options = [
                        "Acne / Blemishes",
                        "Anti Aging",
                        "Dark Circles & Puffiness",
                        "Large & Visible Pores",
                        "Blackheads",
                        "Damaged Skin Barrier",
                        "Hyperpigmentation & Dark Spots",
                        "Redness",
                        "Dullness"
                    ]
                    
                    # Display user's current concerns 
                    current_concerns = [c.title() for c in profile.get("concerns", [])]
                    # Only defaults that are in options (to avoid Streamlit errors)
                    multiselect_defaults = [c for c in current_concerns if c in concerns_options]
                    
                    skin_concerns = st.multiselect(
                        "Skin Concerns",
                        options=concerns_options,
                        default=multiselect_defaults,
                        help="Select from common concerns. You can also add custom ones below."
                    )
                    # Lowercase for storage
                    skin_concerns = [c.lower() for c in skin_concerns]
                    
                    # Optional: custom concerns (comma-separated)
                    custom_concerns = st.text_input(
                        "Other Concerns (comma-separated, optional):",
                        value="",
                        placeholder="e.g., rosacea, eczema, melasma"
                    )
                    # Form submit buttons
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        submitted = st.form_submit_button("💾 Save Changes")
                    with col2:
                        cancel = st.form_submit_button("❌ Cancel")
                    
                    if submitted:
                        # Combine multiselect and custom concerns, all lowercase
                        all_concerns = skin_concerns
                        if custom_concerns:
                            custom_list = [c.strip().lower() for c in custom_concerns.split(",") if c.strip()]
                            all_concerns += custom_list
                        # Remove duplicates
                        all_concerns = list(dict.fromkeys(all_concerns))
                        
                        update_data = {
                            "skin_type": skin_type,
                            "concerns": all_concerns
                        }
                        update_response = requests.patch(
                            f"{API_BASE_URL}/profile",
                            headers=get_auth_header(),
                            json=update_data
                        )
                        
                        if update_response.status_code == 200:
                            response_data = update_response.json()
                            st.success("Profile updated successfully!")
                            st.session_state.edit_mode = False
                            st.rerun()
                        else:
                            st.error("Failed to update profile. Please try again.")
                    
                    if cancel:
                        st.session_state.edit_mode = False
                        st.rerun()
            
            else:
                # View Mode UI
                col1, col2 = st.columns([1, 3])
                
                with col2:
                    st.subheader("Email")
                    st.info(profile.get("email", ""))
                    
                    st.subheader("Skin Type")
                    st.info(profile.get("skin_type", "").capitalize())
                    
                    st.subheader("Skin Concerns")
                    # Pretty display: show as Title Case, joined by comma
                    concerns = [c.title() for c in profile.get("concerns", [])]
                    if concerns:
                        st.info(", ".join(concerns))
                    else:
                        st.info("None specified")
                
                # Edit button
                if st.button("✏️ Edit Profile", key="edit_profile"):
                    st.session_state.edit_mode = True
                    st.rerun()
                    
        else:
            st.error("Failed to load profile data")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        
    # Logout button
    if st.button("🔒 Logout", use_container_width=True, key="profile_logout"):
        logout()
