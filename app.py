import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import os

# --- კონფიგურაცია ---
API_KEY = "AIzaSyDrFdRWcnVeyZ04Y5IWSoiMpIVU2RFXxDk"
MY_PASSWORD = "111979" # <--- შეცვალე ეს შენი სასურველი პაროლით!

genai.configure(api_key=API_KEY)
model = model = genai.GenerativeModel('gemini-1.5-flash-latest')

st.set_page_config(page_title="დაცული დღიური", layout="centered")

# --- პაროლის შემოწმება ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 დაცული დღიური")
    pwd = st.text_input("შეიყვანეთ პაროლი:", type="password")
    if st.button("შესვლა"):
        if pwd == MY_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("პაროლი არასწორია!")
    st.stop()

# --- აპლიკაციის ძირითადი ნაწილი (მხოლოდ სწორი პაროლის შემდეგ) ---
st.title("📝 ჩემი პერსონალური დღიური")
DB_FILE = "diary_db.csv"

if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["თარიღი", "საათი", "ჩანაწერი", "განწყობა"])
    df.to_csv(DB_FILE, index=False)

user_input = st.text_area("რა ხდება დღეს?", placeholder="დაწერე აქ...")

if st.button("შენახვა"):
    if user_input:
        with st.spinner('Gemini აანალიზებს...'):
            prompt = f"Determine the mood in Georgian: {user_input}"
            response = model.generate_content(prompt)
            sentiment = response.text.strip()
            now = datetime.now()
            new_entry = pd.DataFrame([[now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), user_input, sentiment]], 
                                     columns=["თარიღი", "საათი", "ჩანაწერი", "განწყობა"])
            new_entry.to_csv(DB_FILE, mode='a', header=False, index=False)
            st.success("შენახულია!")
            st.rerun()

st.markdown("---")
st.subheader("📜 ისტორია")
if os.path.exists(DB_FILE):
    history_df = pd.read_csv(DB_FILE)
    if not history_df.empty:
        st.dataframe(history_df.sort_values(by=["თარიღი", "საათი"], ascending=False), use_container_width=True)
