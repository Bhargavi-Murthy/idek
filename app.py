from dotenv import load_dotenv
load_dotenv()  # Load environment variables

import streamlit as st
import os
import google.generativeai as genai

# Configure API key
genai.configure(api_key=os.getenv("AIzaSyBpkJUktKt3SytInPIqMbRxH5wMkb34Mzg"))

# Initialize GenerativeModel for Gemini Pro
model = genai.GenerativeModel("gemini-pro")

# Initialize Streamlit app
st.set_page_config(page_title="POOPOO LAND")
st.header("hello nirmala favorite mummy")

input_text = st.text_area("Input: ", "type in things you want to know about.")
submit = st.button("Explain this to a five-year-old")

if submit and input_text:
    response = model.generate_content([input_text, "Explain this to a five year old."])
    st.subheader("The Response is")
    for chunk in response:
        st.write(chunk.text)
