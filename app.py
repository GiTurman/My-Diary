import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import os
from streamlit_mic_recorder import speech_to_text

# --- კონფიგურაცია ---
API_KEY = "AIzaSyDrFdRWcnVeyZ04Y5IWSoiMpIVU2RFXxDk"
MY_PASSWORD = "1" 

# Gemini-ს გამართვა (ვუთითებთ ვერსიას სტაბილურობისთვის)
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="ჭკვიანი დღიური", layout="centered")

# --- პაროლის სისტემა ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 შესვლა")
    pwd = st.text_input("შეიყვანეთ პაროლი:", type="password")
    if st.button("შესვლა"):
        if pwd == MY_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("პაროლი არასწორია!")
    st.stop()

# --- აპლიკაცია ---
st.title("📝 ჩემი პერსონალური დღიური")

# ხმოვანი ჩანაწერი (ქართული ენის მხარდაჭერით)
st.subheader("🎤 ხმოვანი ჩანაწერი")
text_from_speech = speech_to_text(
    language='ka',
    start_prompt="დააჭირე სალაპარაკოდ",
    stop_prompt="შეჩერება",
    key='recorder'
)

# თუ ხმა ამოიცნო, ჩაწეროს ტექსტის ველში
if text_from_speech:
    st.info(f"ამოცნობილი ტექსტი: {text_from_speech}")

user_input = st.text_area("რა ხდება დღეს?", value=text_from_speech if text_from_speech else "", placeholder="დაწერე ან ისაუბრე...")

DB_FILE = "diary_db.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["თარიღი", "საათი", "ჩანაწერი", "განწყობა"]).to_csv(DB_FILE, index=False)

if st.button("💾 შენახვა"):
    if user_input:
        with st.spinner('Gemini აანალიზებს...'):
            sentiment = "უცნობი"
            try:
                # ვცდით სხვადასხვა მოდელს რიგრიგობით
                for model_name in ['gemini-1.5-flash', 'gemini-1.0-pro']:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(f"Describe the mood in one Georgian word: {user_input}")
                        if response.text:
                            sentiment = response.text.strip()
                            break 
                    except:
                        continue
            except Exception:
                sentiment = "AI შეცდომა"

            now = datetime.now()
            new_entry = pd.DataFrame([[now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), user_input, sentiment]], 
                                     columns=["თარიღი", "საათი", "ჩანაწერი", "განწყობა"])
            new_entry.to_csv(DB_FILE, mode='a', header=False, index=False)
            st.success(f"შენახულია! განწყობა: {sentiment}")
            st.rerun()

st.markdown("---")
st.subheader("📜 ჩანაწერები")
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    if not df.empty:
        st.dataframe(df.sort_values(by=["თარიღი", "საათი"], ascending=False), use_container_width=True, hide_index=True)
