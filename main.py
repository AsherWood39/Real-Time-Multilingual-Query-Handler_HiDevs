import streamlit as st
from streamlit.runtime.scriptrunner import RerunException
from streamlit.runtime.scriptrunner.script_runner import add_script_run_ctx
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
from langdetect import detect
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import langcodes
import json
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
    temperature=1.0,
    groq_api_key = GROQ_API_KEY,
    model_name="llama-3.1-8b-instant"
)

with open("languages.json", "r", encoding="utf-8") as f:
    LANGUAGES = json.load(f)

def get_language_name_by_code(code):
    try:
        return langcodes.Language.get(code).language_name()
    except Exception:
        return code 
    
def reset_conversation():
        keys_to_clear = ["user_query", "submitted", "rating"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]    
 
class Functions:
    def __init__(self, llm, languages):
        self.llm = llm
        self.languages = languages
    
    def show_intro(self):
        st.markdown(
                """
                Hello there! I'm your friendly AI assistant, ready to help you out in any language. Here's how I work to make our conversation smooth and easy:
                - I start by detecting the language you're using (if Auto Detect is selected).
                - If needed, I translate your message into English so I can understand it better.
                - Then, I generate a helpful and thoughtful response just for you.
                - Finally, I translate my response back into your preferred language (if anything other than English is selected your output language).
                I'm always here to chat, answer questions, and make your experience as seamless as possible. Let's get started! 
                """
            )
        
    def get_user_inputs(self):
        if st.session_state.get("clear_query", False):
            st.session_state["user_query"] = ""
            st.session_state["clear_query"] = False 

        input_lang = st.selectbox(
            "Input Language (or Auto Detect):", 
            options=list(LANGUAGES.keys()), 
            index = 0,
            help="If Auto Detect is selected, language will be detected automatically"
        )

        output_lang = st.selectbox(
            "Output Language:", 
            options=[lang for lang in LANGUAGES.keys() if lang != "Auto Detect"],
            index=11,
            help="Select the language you want the respond to be in"
        )

        user_query = st.text_area(
            "Enter your query here : ",
            height = 150,
            key="user_query"
        )
        
        return input_lang, output_lang, user_query

    def translate_if_needed(self, user_query, input_lang, output_lang, input_lang_code, output_lang_code):
        if input_lang_code != output_lang_code:
            prompt_str = [
                SystemMessage(content="You are a precise and fluent translation engine. Translate the text exactly and completely from {input_lang} to {output_lang}. Do not add or remove anything."),
                HumanMessage(content=f"Translate this from {input_lang} to {output_lang}:\n{user_query}")
                ]
            response = llm.invoke(prompt_str).content.strip()

            if not response or response.strip() == user_query.strip() or "Translate this" in response:
                st.warning("Translation may have failed. Sending original message to the assistant.")
                response = user_query
        else:
            response = user_query

        return response

    def generate_bot_response(self, text, output_lang):
        prompt = [
            SystemMessage(
                    content=f"""
                    You're a friendly, helpful AI assistant. Respond warmly, clearly, and concisely in {output_lang}.
                    Here are examples of your tone and style:
                        
                    User: I can’t figure out how to reset my password.
                    AI: No worries! Here's how you can reset your password...
                        
                    User: The website is showing an error when I log in.
                    AI: Uh-oh! Let’s fix that. Can you tell me what the error says?
                        
                    Now reply to this message:
                    """),
                    HumanMessage(content=text)
        ]
        return llm.invoke(prompt).content.strip()      
          
    def log_interaction(self, user_query, input_lang, output_lang, translated_text, bot_reply, rating):
        if "log" not in st.session_state:
            st.session_state.log = []

        st.session_state.log.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_prompt": user_query,
            "input_lang": input_lang,
            "output_lang": output_lang,
            "translated": translated_text,
            "reply": bot_reply,
            "rating": rating
        }) 

    def offer_download(self):
        if "log" in st.session_state and st.session_state.log:
            if st.button("Download Log CSV"):
                df = pd.DataFrame(st.session_state.log)
                df.to_csv("translation_log.csv", index=False)
                st.success("Saved as translation_log.csv")
        else:
            st.info("Enter a message and submit it to enable download.")

    def show_result(self, user_query, input_lang, output_lang, translated_text, bot_reply):
        # Show results and rating slider if submitted
        if st.session_state.get("submitted", False):
            # Display last translation and reply
            st.subheader(f"Translated Message ({output_lang}): ")
            st.success(translated_text)

            st.subheader(f"Support Reply ({output_lang}): ")
            st.info(bot_reply)

            st.markdown("---")

            # Rating slider outside button block to track changes
            rating = st.slider("Rate the translation and reply quality : ", 1, 5, st.session_state.rating)
                
            # Update rating in session_state
            if rating != st.session_state.rating:
                st.session_state.rating = rating

            # Show balloons if rating >= 4
            if rating >= 4:
                st.balloons()
                st.success("Thanks for the great rating!")

            # Log interaction for download or further use    
            self.log_interaction(user_query, input_lang, output_lang, translated_text, bot_reply, rating) 

            if st.button("Clear"):
                st.session_state.clear_query = True 
                st.session_state.submitted = False
                reset_conversation()
                st.rerun()

            self.offer_download()            

def main():
    st.title("Real Time Multilingual Query Translator Bot")

    # Initialize session state variables
    if "user_query" not in st.session_state:
        st.session_state.user_query = ""
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "clear_query" not in st.session_state:
        st.session_state.clear_query = False        
    if "rating" not in st.session_state:
        st.session_state.rating = 3  # default rating

    func = Functions(llm=llm, languages=LANGUAGES)

    func.show_intro()

    if "clear_query" not in st.session_state:
        st.session_state.clear_query = False
    
    input_lang, output_lang, user_query = func.get_user_inputs()

    translated_text = ""
    bot_reply = ""

    if st.button("Submit") and user_query.strip():
        input_lang_code = LANGUAGES[input_lang]
        output_lang_code = LANGUAGES[output_lang]

        # Detect language if auto selected
        if input_lang_code == "auto":
            try:
                input_lang_code = detect(user_query)
                st.info(f"Detected language code : `{get_language_name_by_code(input_lang_code)}`")
            except Exception:
                st.error("Language detect failed.")
                return
            
        try:    
            with st.spinner("Translating and generating response..."):
                # Translate query if input/output differ
                translated_text = func.translate_if_needed(user_query, input_lang, output_lang, input_lang_code, output_lang_code)
                # Generate bot reply
                bot_reply = func.generate_bot_response(translated_text, output_lang)

            # Save results in session_state so UI persists on rerun
            st.session_state.submitted = True

        except Exception as e:
            st.error(f"⚠️ An error occurred: {e}")
            return    
            
    func.show_result(user_query, input_lang, output_lang, translated_text, bot_reply)               

if __name__ == "__main__":
    main()         
