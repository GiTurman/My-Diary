import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import os

# --- კონფიგურაცია ---
# ჩასვი შენი API გასაღები აქ
API_KEY = "AIzaSyDrFdRWcnVeyZ04Y5IWSoiMpIVU2RFXxDk"
MY_PASSWORD = "შენი_პაროლი_აქ" # <--- შეცვალე ეს!

# Gemini-ს გამართვა
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="ჩემი დღიური", layout="centered")

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

# --- აპლიკაციის ლოგიკა ---
st.title("📝 ჩემი პერსონალური დღიური")

DB_FILE = "diary_db.csv"

# ბაზის შემოწმება
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["თარიღი", "საათი", "ჩანაწერი", "განწყობა"])
    df.to_csv(DB_FILE, index=False)

user_input = st.text_area("რა ხდება დღეს?", placeholder="დაწერე აქ...")

if st.button("💾 შენახვა"):
    if user_input:
        sentiment = "Gemini-ს გარეშე" # საწყისი მნიშვნელობა
        
        # ვცდილობთ Gemini-ს გამოყენებას
        try:
            # ვტესტავთ ყველაზე მარტივ მოდელს
            model = genai.GenerativeModel('gemini-pro') 
            response = model.generate_content(f"Determine mood in one Georgian word: {user_input}")
            if response.text:
                sentiment = response.text.strip()
        except Exception:
            # თუ Gemini-მ აურია, პროგრამა არ გაითიშება
            sentiment = "შენახულია (AI-ს გარეშე)"

        # მონაცემების მომზადება
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        
        new_entry = pd.DataFrame([[date_str, time_str, user_input, sentiment]], 
                                 columns=["თარიღი", "საათი", "ჩანაწერი", "განწყობა"])
        
        # შენახვა ფაილში
        new_entry.to_csv(DB_FILE, mode='a', header=False, index=False)
        st.success("ჩანაწერი წარმატებით შეინახა!")
        st.rerun()
    else:
        st.warning("გთხოვთ, შეიყვანოთ ტექსტი.")

st.markdown("---")

# ისტორიის ჩვენება
st.subheader("📜 წინა ჩანაწერები")
if os.path.exists(DB_FILE):
    try:
        history_df = pd.read_csv(DB_FILE)
        if not history_df.empty:
            # უახლესი ჩანაწერები ზემოთ
            history_df = history_df.sort_values(by=["თარიღი", "საათი"], ascending=False)
            st.dataframe(history_df, use_container_width=True, hide_index=True)
        else:
            st.info("ჩანაწერები ჯერ არ არის.")
    except Exception:
        st.error("მონაცემების წაკითხვის შეცდომა.")
