import streamlit as st
import requests
from utils import get_auth_header, get_saved_routines, display_routine,API_BASE_URL


def render():
    st.title("✨ Your Personalized Skincare Routine")
    saved_routines = get_saved_routines()
    if saved_routines:
        routine_names = [f"{r['time_of_day']} Routine - {r['created_at'][:10]}" 
                       for r in saved_routines]
        selected_routine = st.selectbox(
            "Select Saved Routine",
            routine_names,
            index=0
        )
        selected_index = routine_names.index(selected_routine)
        display_routine(saved_routines[selected_index])

        st.subheader("Generate New Routine")
        st.markdown("---")
    
    
    try:
        profile = requests.get(
            f"{API_BASE_URL}/profile",
            headers=get_auth_header()
        ).json()
        skin_type = profile["skin_type"].capitalize()
        concerns = [c.capitalize() for c in profile["concerns"]]
        
        st.subheader(f"🧴 Skin Profile: {skin_type} skin")
        st.caption(f"⚡ Concerns: {', '.join(concerns) if concerns else 'None'}")
    except:
        st.warning("Could not load skin profile")
        return
    
    st.markdown("---")
    
    if st.button("✨ Generate AM & PM Routine", use_container_width=True):
    
        with st.spinner("🧪 Creating your personalized routine with AI..."):
            try:
                # Generate AM routine
                am_response = requests.post(
                    f"{API_BASE_URL}/generate-routine",
                    headers=get_auth_header(),
                    json={"time_of_day": "AM"}
                )
                am_data = am_response.json() if am_response.status_code == 200 else None
                
                # Generate PM routine
                pm_response = requests.post(
                    f"{API_BASE_URL}/generate-routine",
                    headers=get_auth_header(),
                    json={"time_of_day": "PM"}
                )
                pm_data = pm_response.json() if pm_response.status_code == 200 else None
                
                st.session_state.routine_data = {
                    "AM": am_data,
                    "PM": pm_data
                }
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    if st.session_state.get("routine_data"):
        am_data = st.session_state.routine_data.get("AM")
        pm_data = st.session_state.routine_data.get("PM")
        
        am_col, pm_col = st.columns(2)
        
        with am_col:
          if am_data and "routine" in am_data:
            st.subheader("🌞 Morning Routine (AM)")
            for step in am_data["routine"]:
                st.markdown(f"**{step['step'].capitalize()}: {step['product']}**")
                st.write(step["description"])
                url = step.get("brand_url") or step.get("link") or "#"
                if url != "#":
                  st.markdown(f"[Visit Brand Website]({url})")
                st.markdown("---")
                
        with pm_col:
          if pm_data and "routine" in pm_data:
            st.subheader("🌙 Evening Routine (PM)")
            for step in pm_data["routine"]:
                st.markdown(f"**{step['step'].capitalize()}: {step['product']}**")
                st.write(step["description"])
                url = step.get("brand_url") or step.get("link") or "#"
                if url != "#":
                  st.markdown(f"[Visit Brand Website]({url})")
                st.markdown("---")