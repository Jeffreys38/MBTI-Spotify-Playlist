import streamlit as st
import json
import pandas as pd
import google.generativeai as genai 

# SETUP
API = st.secrets["API"]
genai.configure(api_key = API)

# READ DATA
@st.cache_data
def load_mbti():
    return pd.read_csv("./csv/combined_mbti_df.csv")

combined_mbti_df = load_mbti()
mbti_types = combined_mbti_df["mbti"].drop_duplicates().to_numpy()

# LOAD CONFIG
with open("config.json", "r", encoding = "utf-8") as f:
    config = json.load(f)

    initial_message = config.get("initial-message")

    bot_name = config.get("bot-name")
    bot_avt = config.get("bot-avt")
    
    user_avt = config.get("user-avt")

# GENERATE MODEL
@st.cache_resource
def load_model():
    return genai.GenerativeModel("gemini-1.5-flash",
                system_instruction = f"""Bạn tên là ${bot_name}, nhiệm vụ của bạn là tư vấn cho người dùng
                về loại tính cách của họ và giải đáp các thắc mắc về 16 loại tính cách MBTI.

                Gồm có 16 loại tính cách ${', '.join(mbti_types)}, bạn cần phân tích những functions như Ni, Ti, Fi, Si,
                Ne, Te, Fe, Se trong MBTI của người dùng. Hãy trả lời người dùng bằng tiếng Việt sao cho dễ hiểu,
                kèm theo ví dụ thực tế có liên quan.

                Bạn cần trả lời tin nhắn mới nhất và sử dụng những tin nhắn trước làm trí nhớ của mình
                """)

model = load_model()

# TITLE
st.title("Which MBTI is your Spotify playlist?")

# CALL AI
def chat_bot():
    if "history" not in st.session_state:
        st.session_state.history = [{
            "role": "assitant",
            "content": initial_message,
            "avt": bot_avt
        }]

    if "bot_memory" not in st.session_state:
        st.session_state.bot_memory = []

    for message in st.session_state.history:
        with st.chat_message(message["role"], avatar = message["avt"]):
            st.write(message["content"])

    prompt = st.chat_input("Your reply")
    if prompt:
        st.session_state.history.append({
            "role": "user",
            "content": prompt,
            "avt": user_avt
        })

        with st.chat_message("user", avatar = user_avt):
            st.markdown("You")
            st.write(prompt)

        bot_response = model.generate_content(f"Tin nhắn trước: {st.session_state.bot_memory}, bạn cần trả lời: {prompt} (người dùng nhắn)").text

        print(st.session_state.bot_memory)
        
        st.session_state.history.append({
            "role": "assitant",
            "content": bot_response,
            "avt": bot_avt
        })

        with st.chat_message("assitant", avatar = bot_avt):
            st.markdown(bot_name)
            st.write(bot_response)

        st.session_state.bot_memory.append(f"{prompt} (người dùng nhắn)")
        st.session_state.bot_memory.append(f"{bot_response} (bạn nhắn)")

if __name__ == "__main__":
    chat_bot()