import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import os

# Gemini-ს კონფიგურაცია შენი გასაღებით
API_KEY = "AIzaSyDrFdRWcnVeyZ04Y5IWSoiMpIVU2RFXxDk"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# გვერდის ვიზუალი
st.set_page_config(page_title="ჩემი ჭკვიანი დღიური", layout="centered")
st.title("📝 პერსონალური დღიური")
st.markdown("---")

# ფაილი მონაცემების შესანახად
DB_FILE = "diary_db.csv"

# თუ ფაილი არ არსებობს, ვქმნით მას
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["თარიღი", "საათი", "ჩანაწერი", "განწყობა"])
    df.to_csv(DB_FILE, index=False)

# ჩანაწერის დამატების სექცია
with st.container():
    st.subheader("ახალი ჩანაწერი")
    user_input = st.text_area("რა ხდება შენს თავს?", height=150, placeholder="დღეს ძალიან კარგი დღე იყო...")
    
    if st.button("💾 შენახვა", use_container_width=True):
        if user_input:
            with st.spinner('Gemini ამუშავებს ჩანაწერს...'):
                try:
                    # Gemini აანალიზებს ტექსტს
                    prompt = f"Determine the mood of this diary entry in Georgian (one word): {user_input}"
                    response = model.generate_content(prompt)
                    sentiment = response.text.strip()
                    
                    # დროის ფიქსაცია
                    now = datetime.now()
                    date_str = now.strftime("%Y-%m-%d")
                    time_str = now.strftime("%H:%M")
                    
                    # მონაცემების ბაზაში ჩაწერა
                    new_entry = pd.DataFrame([[date_str, time_str, user_input, sentiment]], 
                                             columns=["თარიღი", "საათი", "ჩანაწერი", "განწყობა"])
                    new_entry.to_csv(DB_FILE, mode='a', header=False, index=False)
                    
                    st.success("ჩანაწერი წარმატებით შეინახა!")
                    st.balloons()
                except Exception as e:
                    st.error(f"მოხდა შეცდომა: {e}")
        else:
            st.warning("გთხოვთ, ჯერ შეიყვანოთ ტექსტი.")

st.markdown("---")

# ისტორიის სექცია
st.subheader("📜 ჩანაწერების ისტორია")

if os.path.exists(DB_FILE):
    history_df = pd.read_csv(DB_FILE)
    if not history_df.empty:
        # დახარისხება უახლესიდან ძველისკენ (თარიღის და საათის მიხედვით)
        history_df = history_df.sort_values(by=["თარიღი", "საათი"], ascending=False)
        
        # ცხრილის ჩვენება
        st.dataframe(history_df, use_container_width=True, hide_index=True)
    else:
        st.info("ჯერჯერობით ჩანაწერები არ არის.")
