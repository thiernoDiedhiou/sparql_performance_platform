"""
Test simple pour vérifier si le HTML fonctionne dans Streamlit
"""
import streamlit as st

st.set_page_config(page_title="Test Guide", layout="wide")

st.markdown("## Test HTML Rendering")

# Test 1: HTML simple
test_html = """
<div style="
    background: #f0f0f0;
    border: 2px solid #007bff;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
">
    <h3 style="color: #007bff;">Test HTML</h3>
    <p>Si vous voyez ce texte stylisé, le HTML fonctionne !</p>
</div>
"""

st.markdown("### Test 1: HTML avec unsafe_allow_html=True")
st.markdown(test_html, unsafe_allow_html=True)

st.markdown("### Test 2: HTML sans unsafe_allow_html")
st.markdown(test_html)

st.markdown("### Test 3: Markdown standard")
st.markdown("- Item 1\n- Item 2\n- Item 3")
