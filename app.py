import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import os
from streamlit_mic_recorder import speech_to_text
from PIL import Image

# --- კონფიგურაცია ---
API_KEY = "AIzaSyDrFdRWcnVeyZ04Y5IWSoiMpIVU2RFXxDk"
genai.configure(api_key=API_KEY)

# მომხმარებლების ბაზა (მომხმარებელი: პაროლი)
USERS = {
    "giorgi": "1234",
    "ბაიკო": "1234",
    "ანა": "1234",
    "admin": "0000"
}

st.set_page_config(page_title="ჩემი მრავალფუნქციური დღიური", layout="centered")

# --- ავტორიზაცია ---
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    st.title("🔐 შესვლა")
    username = st.text_input("მომხმარებელი:")
    password = st.text_input("პაროლი:", type="password")
    if st.button("შესვლა"):
        if username in USERS and USERS[username] == password:
            st.session_state["user"] = username
            st.rerun()
        else:
            st.error("არასწორი მონაცემები!")
    st.stop()

# --- აპლიკაციის შიგთავსი ---
current_user = st.session_state["user"]
st.sidebar.write(f"👤 მომხმარებელი: **{current_user}**")
if st.sidebar.button("გამოსვლა"):
    st.session_state["user"] = None
    st.rerun()

st.title(f"📝 {current_user}-ს დღიური")

# ფაილის სახელი თითოეული მომხმარებლისთვის ინდივიდუალურია
DB_FILE = f"diary_{current_user}.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["თარიღი", "საათი", "ჩანაწერი", "განწყობა"]).to_csv(DB_FILE, index=False)

# 1. ხმოვანი ნაწილი
st.subheader("🎤 ისაუბრე")
text_from_speech = speech_to_text(language='ka', start_prompt="ჩაწერა", key='recorder')

# 2. ტექსტური ნაწილი
user_input = st.text_area("რა ხდება დღეს?", value=text_from_speech if text_from_speech else "")

# 3. სურათის ატვირთვა
uploaded_file = st.file_uploader("დაამატე ფოტო (მცირე რეზოლუციით)", type=['jpg', 'png', 'jpeg'])
if uploaded_file:
    img = Image.open(uploaded_file)
    # რეზოლუციის შემცირება საჩვენებლად
    img.thumbnail((300, 300))
    st.image(img, caption="ატვირთული ფოტო")

# 4. შენახვა
if st.button("💾 ჩაწერა დღიურში"):
    if user_input:
        sentiment = "..."
        try:
            # Gemini-ს მოდელის ტესტირება
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"Analyze mood in Georgian: {user_input}")
            sentiment = response.text.strip()
        except:
            sentiment = "შენახულია AI-ს გარეშე"

        now = datetime.now()
        new_entry = pd.DataFrame([[now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), user_input, sentiment]], 
                                 columns=["თარიღი", "საათი", "ჩანაწერი", "განწყობა"])
        new_entry.to_csv(DB_FILE, mode='a', header=False, index=False)
        st.success("წარმატებით შეინახა!")
        st.balloons()
        st.rerun()

st.markdown("---")
st.subheader("📜 ჩემი ჩანაწერები")
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    st.dataframe(df.sort_values(by=["თარიღი", "საათი"], ascending=False), use_container_width=True, hide_index=True)
