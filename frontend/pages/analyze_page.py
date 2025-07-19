import streamlit as st
import requests
from utils import get_auth_header,API_BASE_URL


def render():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span class="section-header-icon">🔍</span><h2>Analyze Skincare Product</h2></div>', unsafe_allow_html=True)
    st.markdown("Upload an image of a skincare product's ingredient list to get personalized analysis")
    # File uploader
    uploaded_file = st.file_uploader(
        "**Drag & drop or browse files**",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    st.subheader("🔍 Or search by product name")
    
    with st.form("product_search_form"):
        product_name = st.text_input(
            "Enter product name (e.g., 'CeraVe Foaming Facial Cleanser')",
            placeholder="Brand + Product Name"
        )
        submitted = st.form_submit_button("Search and Analyze", use_container_width=True)
        
        if submitted and product_name:
            with st.spinner(f"🔍 Searching for {product_name} and analyzing ingredients..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/analyze-product-by-name",
                        headers=get_auth_header(),
                        json={"product_name": product_name}
                    )
                    
                    if response.status_code == 200:
                        st.session_state.report = response.json()
                        st.session_state.analyzed = True
                        st.success("🎉 Analysis complete!")
                        st.balloons()
                    else:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"Analysis failed: {error_detail}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    if uploaded_file is not None:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(uploaded_file, caption="Uploaded Product", width=250)
        with col2:
            st.info("Tips for best results:")
            st.markdown("- 📸 Capture in good lighting")
            st.markdown("- 🔍 Ensure text is clear and in focus")
            st.markdown("- 📜 Flat surfaces work best")
        
        if st.button("Analyze Ingredients", use_container_width=True, key="analyze_btn"):
            with st.spinner("🔬 Analyzing ingredients. This may take 15-30 seconds..."):
                try:
                    file_bytes = uploaded_file.getvalue()
                    files = {"image": (uploaded_file.name, file_bytes, uploaded_file.type)}
                    
                    response = requests.post(
                        f"{API_BASE_URL}/analyze-product",
                        headers=get_auth_header(),
                        files=files
                    )
                    
                    if response.status_code == 200:
                        st.session_state.report = response.json()
                        st.session_state.analyzed = True
                        st.success("🎉 Analysis complete!")
                        st.balloons()
                    elif response.status_code == 400:
                        st.error("⚠️ No ingredients found in the image. Please ensure:")
                        st.markdown("- The ingredient list is clearly visible")
                        st.markdown("- Text is not blurry or obscured")
                        st.markdown("- Try capturing in better lighting")
                    else:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"Analysis failed: {error_detail}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.analyzed and st.session_state.report:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header"><span class="section-header-icon">📝</span><h2>Product Analysis Report</h2></div>', unsafe_allow_html=True)
        
        report = st.session_state.report
        analysis = report.get("analysis", {})
        overall = analysis.get("overall_assessment", {})
        ingredients = analysis.get("ingredients", [])
        
        safety_rating = overall.get("safety_rating", "").lower()
        safety_color = {
            "safe": "🟢",
            "caution": "🟡",
            "unsafe": "🔴"
        }.get(safety_rating, "⚪")
        
        st.subheader("Overall Assessment")
        
        cols = st.columns(5)
        metrics = [
            ("Safety Rating", f"{safety_color} {overall.get('safety_rating', 'N/A')}"),
            ("Suitability", f"{overall.get('suitability_score', 'N/A')}/5"),
            ("Barrier Impact", overall.get('barrier_impact', 'N/A')),
            ("Allergy Risk", overall.get('allergy_risk', 'N/A')),
            ("Key Concerns", f"{len(overall.get('key_concerns', []))} found")
        ]
        
        for i, (label, value) in enumerate(metrics):
            with cols[i]:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        with st.expander("💡 Personalized Summary", expanded=True):
            st.write(overall.get("personalized_notes", "No notes available"))

        if analysis.get("alternative_products"):
            st.subheader("♻️ Recommended Alternative Products")
            st.markdown("Here are products that might work better for your skin type:")
            
            for alt in analysis["alternative_products"]:
                with st.expander(f"**{alt['brand']} - {alt['product']}** ({alt.get('type', 'commercial').capitalize()})"):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown("**Why better?**")
                    with col2:
                        st.markdown(alt['reason'])
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown("**Key ingredients:**")
                    with col2:
                        st.markdown(", ".join(alt['key_ingredients']))
        st.subheader("⚠️ Ingredient Compatibility Guide")
        st.markdown("""
        | Active Ingredient | Ideal Time | Don't Mix With                 |
        |-------------------|------------|--------------------------------|
        | Vitamin C         | AM         | Retinol, Benzoyl Peroxide, AHA/BHA |
        | Niacinamide       | AM/PM      | (Caution with L-Ascorbic Acid) |
        | Retinol           | PM         | Vitamin C, AHA/BHA, Benzoyl Peroxide |
        | AHA/BHA           | PM         | Retinol, Vitamin C             |
        | Benzoyl Peroxide  | AM         | Retinol, Vitamin C             |
        """)
        st.caption("Note: Always patch test new products and consult a dermatologist for personalized advice.")


        st.subheader("Ingredient Analysis")
        st.caption(f"Found {len(ingredients)} ingredients")
        
        concerning_ingredients = [i for i in ingredients if i.get('special_concerns')]
        safe_ingredients = [i for i in ingredients if not i.get('special_concerns')]
        
        if concerning_ingredients:
            st.subheader("⚠️ Ingredients with Concerns", anchor="concerns")
            for ingredient in concerning_ingredients:
                concerns = ingredient.get('special_concerns', [])
                st.markdown(
                    f"""
                    <div class="ingredient-card">
                        <div class="ingredient-name">{ingredient.get('name', 'Unknown')}</div>
                        <div class="ingredient-function">Function: {ingredient.get('function', 'N/A')}</div>
                        <div class="ingredient-concern">Concerns: {', '.join(concerns)}</div>
                        <div class="ingredient-notes">Notes: {ingredient.get('personalized_notes', 'N/A')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        if safe_ingredients:
            st.subheader("✅ Safe Ingredients")
            for ingredient in safe_ingredients:
                st.markdown(
                    f"""
                    <div class="ingredient-card">
                        <div class="ingredient-name">{ingredient.get('name', 'Unknown')}</div>
                        <div class="ingredient-function">Function: {ingredient.get('function', 'N/A')}</div>
                        <div class="ingredient-notes">Notes: {ingredient.get('personalized_notes', 'N/A')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span class="section-header-icon">💬</span><h2>Ask Skincare Assistant</h2></div>', unsafe_allow_html=True)
    st.caption("Ask questions about your skincare products and get personalized advice")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about your skincare product..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    headers=get_auth_header(),
                    json={"question": prompt}
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    assistant_response = response_data.get("response", "I couldn't process that request")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_response
                    })
                    
                    with st.chat_message("assistant"):
                        st.markdown(assistant_response)
                else:
                    st.error("Failed to get response from assistant")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
      