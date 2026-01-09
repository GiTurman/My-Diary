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

# მომხმარებლები
USERS = {"giorgi": "1234", "admin": "0000"}

st.set_page_config(page_title="AI Research Diary", layout="centered")

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

current_user = st.session_state["user"]
st.title(f"🚀 {current_user}-ს ინტელექტუალური დღიური")

# 🎤 ხმოვანი და ტექსტური შეყვანა
st.subheader("🎤 დასვი კითხვა ან აღწერე დღე")
text_from_speech = speech_to_text(language='ka', start_prompt="ჩაწერა (ისაუბრე)", key='recorder')
user_input = st.text_area("ტექსტი:", value=text_from_speech if text_from_speech else "", height=100)

# 🖼️ სურათის ატვირთვა
uploaded_file = st.file_uploader("ჩააგდე ფოტო", type=['jpg', 'png', 'jpeg'])

# 📂 ბაზის გამართვა
DB_FILE = f"diary_{current_user}.csv"
COLUMNS = ["თარიღი", "საათი", "ჩანაწერი", "განწყობა", "AI_პასუხი"]

if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=COLUMNS).to_csv(DB_FILE, index=False)

if st.button("💾 შენახვა და AI ძიება"):
    if user_input:
        with st.spinner('Gemini იძიებს ინფორმაციას...'):
            sentiment = "ანალიზი..."
            ai_response = "..."
            
            try:
                # ვიყენებთ Flash მოდელს, რომელიც სწრაფია და კარგად ეძებს ინფორმაციას
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                შენ ხარ პირადი ასისტენტი და მკვლევარი.
                მომხმარებელმა დაწერა: "{user_input}"
                დავალება:
                1. თუ ტექსტში არის კითხვა (მაგ: "ვინ არის...", "როგორ...", "რა არის..."), მოიძიე უახლესი ინფორმაცია და უპასუხე დეტალურად.
                2. თუ არის უბრალოდ დღიურის ჩანაწერი, გაუკეთე მოკლე ანალიზი.
                3. განსაზღვრე განწყობა (ერთი სიტყვით).
                4. თუ შესაძლებელია, დაამატე სასარგებლო რჩევა ან საინტერესო ფაქტი.
                
                პასუხი დააბრუნე ასე:
                SENTIMENT: [განწყობა]
                ANSWER: [შენი პასუხი ან კვლევის შედეგი]
                """
                
                response = model.generate_content(prompt)
                res_text = response.text
                
                # ინფორმაციის ამოღება პასუხიდან
                if "SENTIMENT:" in res_text and "ANSWER:" in res_text:
                    sentiment = res_text.split("SENTIMENT:")[1].split("ANSWER:")[0].strip()
                    ai_response = res_text.split("ANSWER:")[1].strip()
                else:
                    ai_response = res_text

            except Exception as e:
                st.error(f"კავშირის შეცდომა: {e}")
                sentiment = "შეცდომა"
                ai_response = "AI ამჟამად მიუწვდომელია, მაგრამ ჩანაწერი შენახულია."

            # შენახვა
            now = datetime.now()
            new_data = [now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), user_input, sentiment, ai_response]
            df_new = pd.DataFrame([new_data], columns=COLUMNS)
            df_new.to_csv(DB_FILE, mode='a', header=False, index=False)
            
            st.success("მონაცემები განახლდა!")
            st.rerun()

st.markdown("---")
st.subheader("📚 ჩანაწერების არქივი")

if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    if not df.empty:
        # ვაჩვენებთ ჩანაწერებს ბარათების სახით
        for i, row in df.sort_values(by=["თარიღი", "საათი"], ascending=False).iterrows():
            with st.container():
                st.markdown(f"### 🗓️ {row['თარიღი']} | {row['საათი']}")
                st.write(f"**ჩანაწერი:** {row['ჩანაწერი']}")
                st.success(f"🤖 **AI პასუხი & კვლევა:**\n\n{row['AI_პასუხი']}")
                st.caption(f"📊 განწყობა: {row['განწყობა']}")
                st.divider()
