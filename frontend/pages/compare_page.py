import streamlit as st
import base64
import requests
from utils import get_auth_header, display_comparison_results,API_BASE_URL

def render():
    st.title("🔄 Compare Skincare Products")
    st.markdown("Compare two products using any input method")
    col1, col2 = st.columns(2)
    products = {}
    with col1:
        st.subheader("Product 1")
        input_type1 = st.radio("Input method:", 
                              ["Image", "Text"],
                              key="input1",
                              horizontal=True)
        
        if input_type1 == "Image":
            uploaded_file1 = st.file_uploader("Upload product image", 
                                             type=["jpg", "jpeg", "png"],
                                             key="file1")
            if uploaded_file1:
                products["product1"] = {
                    "input_type": "image",
                    "input_data": base64.b64encode(uploaded_file1.getvalue()).decode("utf-8")
                }
                st.image(uploaded_file1, width=200)
                
        else:  # Text
            text_input1 = st.text_area("Enter product name or ingredients", 
                                     height=150,
                                     key="text1")
            if text_input1:
                products["product1"] = {
                    "input_type": "text",
                    "input_data": text_input1
                }
    
    with col2:
        st.subheader("Product 2")
        input_type2 = st.radio("Input method:", 
                              ["Image", "Text"],
                              key="input2",
                              horizontal=True)
        
        if input_type2 == "Image":
            uploaded_file2 = st.file_uploader("Upload product image", 
                                             type=["jpg", "jpeg", "png"],
                                             key="file2")
            if uploaded_file2:
                products["product2"] = {
                    "input_type": "image",
                    "input_data": base64.b64encode(uploaded_file2.getvalue()).decode("utf-8")
                }
                st.image(uploaded_file2, width=200)
                
        else:  # Text
            text_input2 = st.text_area("Enter product name or ingredients", 
                                     height=150,
                                     key="text2")
            if text_input2:
                products["product2"] = {
                    "input_type": "text",
                    "input_data": text_input2
                }
    
    st.markdown("---")
    
    if st.button("Compare Products", use_container_width=True,
                disabled=len(products) < 2):
        with st.spinner("Analyzing products with AI agent..."):
            try:
                # First analyze both products
                analysis_results = {}
                product_url={}
                for key, product in products.items():
                    response = requests.post(
                        f"{API_BASE_URL}/analyze-product-agent",
                        headers=get_auth_header(),
                        json={
                            "input_type": product["input_type"],
                            "input_data": product["input_data"]
                        }
                    )
                    if response.status_code == 200:
                        analysis_results[key] = response.json()

                        if 'source_url' in analysis_results[key]:
                            product_url[key] = analysis_results[key]['source_url']
                            print("from frontend",product_url[key])
                    
                    else:
                 
                        st.error(f"Analysis failed for {key}: {response.text}")


                # Then compare them
                if len(analysis_results) == 2:
                    compare_response = requests.post(
                        f"{API_BASE_URL}/compare-products",
                        headers=get_auth_header(),
                        json={
                            "product1": analysis_results["product1"],
                            "product2": analysis_results["product2"]
                        }
                    )
                    
                    if compare_response.status_code == 200:
                        comparison = compare_response.json()
                        display_comparison_results(comparison, analysis_results)
                    else:
                        st.error(f"Comparison failed: {compare_response.text}")
                else:
                    st.error("Failed to analyze both products")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")