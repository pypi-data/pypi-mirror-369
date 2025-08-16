# app/main.py
import streamlit as st
from llm_interface.explain_with_gpt import explain_model_results

st.title("AI Model QA Assistant")

api_key = st.text_input("Enter OpenAI API Key", type="password")
if api_key:
    if st.button("Explain My Model"):
        explanation = explain_model_results(api_key)
        st.markdown(explanation)
