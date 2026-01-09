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

# მომხმარებლების ბაზა
USERS = {"giorgi": "1234", "admin": "0000"}

st.set_page_config(page_title="AI Smart Diary", layout="centered")

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

current_user = st.session_state["user"]
st.title(f"📝 {current_user}-ს ჭკვიანი დღიური")

# 1. ხმოვანი და ტექსტური შეყვანა
st.subheader("🎤 ჩაწერე ან ისაუბრე")
text_from_speech = speech_to_text(language='ka', start_prompt="ჩაწერა", key='recorder')
user_input = st.text_area("რა ხდება დღეს?", value=text_from_speech if text_from_speech else "", height=150)

# 2. სურათის ატვირთვა
uploaded_file = st.file_uploader("დაამატე ფოტო", type=['jpg', 'png', 'jpeg'])

# 3. შენახვის ლოგიკა
DB_FILE = f"diary_{current_user}.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["თარიღი", "საათი", "ჩანაწერი", "განწყობა", "AI_კომენტარი"]).to_csv(DB_FILE, index=False)

if st.button("💾 შენახვა და AI ანალიზი"):
    if user_input:
        with st.spinner('Gemini ფიქრობს...'):
            sentiment = "ნეიტრალური"
            ai_comment = "კითხვა არ დასმულა"
            
            try:
                # მოდელის კონფიგურაცია
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                # ინსტრუქცია Gemini-სთვის
                prompt = f"""
                შენ ხარ დღიურის ასისტენტი. გააანალიზე ეს ტექსტი: "{user_input}"
                1. განსაზღვრე განწყობა ერთი სიტყვით (ქართულად).
                2. თუ ტექსტში დასმულია კითხვა, უპასუხე ამომწურავად და საინტერესოდ. 
                თუ კითხვა არ არის, დაწერე მოკლე გამამხნევებელი კომენტარი.
                პასუხი დააბრუნე ფორმატით: 
                განწყობა: [აქ ჩაწერე]
                კომენტარი: [აქ ჩაწერე]
                """
                
                response = model.generate_content(prompt)
                full_response = response.text
                
                # პასუხის დანაწევრება
                if "განწყობა:" in full_response and "კომენტარი:" in full_response:
                    sentiment = full_response.split("განწყობა:")[1].split("კომენტარი:")[0].strip()
                    ai_comment = full_response.split("კომენტარი:")[1].strip()
                else:
                    ai_comment = full_response

            except Exception as e:
                st.error(f"AI შეცდომა: {e}")
                sentiment = "AI შეცდომა"
                ai_comment = "ვერ მოხერხდა პასუხის გენერაცია"

            # ბაზაში ჩაწერა
            now = datetime.now()
            new_entry = pd.DataFrame([[
                now.strftime("%Y-%m-%d"), 
                now.strftime("%H:%M"), 
                user_input, 
                sentiment, 
                ai_comment
            ]], columns=["თარიღი", "საათი", "ჩანაწერი", "განწყობა", "AI_კომენტარი"])
            
            new_entry.to_csv(DB_FILE, mode='a', header=False, index=False)
            st.success("ჩანაწერი შენახულია!")
            st.rerun()

st.markdown("---")
st.subheader("📜 ჩანაწერების ისტორია")
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    if not df.empty:
        for index, row in df.sort_values(by=["თარიღი", "საათი"], ascending=False).iterrows():
            with st.expander(f"📅 {row['თარიღი']} | 🕒 {row['საათი']} | {row['განწყობა']}"):
                st.write(f"**ჩანაწერი:** {row['ჩანაწერი']}")
                st.info(f"🤖 **Gemini-ს პასუხი:** {row['AI_კომენტარი']}")
