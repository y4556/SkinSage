import streamlit as st
from utils import authenticate, signup_user,inject_custom_css
import time

def render():
    st.markdown('<div class="login-background"></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-content">', unsafe_allow_html=True)
    st.markdown('<div class="title-container">'
            '<h1 class="brand-title">SKINSAGE</h1>'
            '<p class="brand-tagline">Your Personalized Skincare Analysis Assistant</p>'
            '</div>', unsafe_allow_html=True)
    # Sephora-aligned skin concerns
    CONCERNS = [
        "Acne / Blemishes",
        "Anti Aging",
        "Dark Circles & Puffiness",
        "Large & Visible Pores",
        "Blackheads",
        "Damaged Skin Barrier",
        "Hyperpigmentation & Dark Spots",
        "Redness"
    ]
    
    if st.session_state.auth_page == "login":
        with st.form("login_form"):
            st.markdown('<h3 class="form-title">SIGN IN</h3>', unsafe_allow_html=True)
            # st.subheader("Sign in to your account")
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if authenticate(email, password):
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
        
        st.markdown("---")
        st.write("Don't have an account?")
        if st.button("Create Account", use_container_width=True, key="create_account_btn"):
            st.session_state.auth_page = "signup"
            st.rerun()
    else:
        with st.form("signup_form"):
            st.markdown('<h3 class="form-title">CREATE ACCOUNT</h3>', unsafe_allow_html=True)
            # st.subheader("Create your account")
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            
            # Skin type selection
            skin_type = st.selectbox(
                "Skin Type",
                ["Normal", "Dry", "Oily", "Combination", "Sensitive"],
                index=0
            )
            
            # Skin concerns with Sephora-aligned options
            st.subheader("Skin Concerns")
            st.caption("Select all that apply to you")
            
            concerns = st.multiselect(
                "Common Skin Concerns:",
                CONCERNS,
                help="These align with Sephora's concern categories for better recommendations"
            )
            
            # Optional custom concerns
            with st.expander("+ Add Specific Concerns (Optional)"):
                custom_concerns = st.text_area(
                    "Describe any specific skin concerns not listed above:",
                    placeholder="e.g., rosacea, eczema, melasma",
                    help="Our AI will map these to the closest Sephora categories"
                )
            
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if submitted:
                # Process custom concerns
                custom_list = []
                if custom_concerns:
                    custom_list = [c.strip().lower() for c in custom_concerns.split(",") if c.strip()]
                
                # Combine concerns
                all_concerns = [c.lower() for c in concerns] + custom_list

                user_data = {
                    "email": email,
                    "password": password,
                    "skin_type": skin_type.lower(),
                    "concerns": all_concerns
                }
                
                if signup_user(user_data):
                    if authenticate(email, password):
                        st.success("Account created and logged in successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Account created but login failed. Please log in manually.")
                else:
                    st.error("Account creation failed. Please try again.")
        
        st.markdown("---")
        st.write("Already have an account?")
        if st.button("Back to Login", use_container_width=True, key="back_to_login"):
            st.session_state.auth_page = "login"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)  # Close center-container
    
