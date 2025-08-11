import google.generativeai as genai
import streamlit as st
import os
import time  # For implementing retry logic

# Configure Streamlit page settings
st.set_page_config(
    page_title="Gemini 챗봇",
    page_icon=":robot_face:",  # Favicon emoji
    layout="wide",  # Page layout option
)

st.title("Gemini 챗봇")

@st.cache_resource
def load_model():
    API_KEY = os.getenv("google_api_key")

    # Set up Google Gemini AI model
    genai.configure(api_key=API_KEY)
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        print("모델 로딩...")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        st.error(f"Failed to load the model. Please check your API key and network connection. Error: {e}")
        return None  # Return None if the model fails to load

model = load_model()

if model is None: # Exit if the model didn't load
    st.stop()


if "chat_session" not in st.session_state:
    try:
        st.session_state["chat_session"] = model.start_chat(history=[])
    except Exception as e:
        st.error(f"Failed to start chat session: {e}")
        st.stop()


for content in st.session_state.chat_session.history:
    with st.chat_message("ai" if content.role == "model" else "user"):
        st.markdown(content.parts[0].text)

if prompt := st.chat_input("메시지를 입력하세요."):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("ai"):
        message_placeholder = st.empty()
        full_response = ""
        with st.spinner("메시지 처리 중입니다."):
            retries = 3
            for attempt in range(retries):
                try:
                    response = st.session_state.chat_session.send_message(prompt, stream=True)
                    for chunk in response:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response)
                    break  # If successful, exit the retry loop
                except Exception as e:
                    print(f"Attempt {attempt+1} failed: {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    if attempt == retries - 1:
                        st.error(f"Failed to get a response after {retries} attempts. Error: {e}")
                        message_placeholder.markdown("An error occurred while processing your request.")
                    else:
                        print("Retrying...") 

