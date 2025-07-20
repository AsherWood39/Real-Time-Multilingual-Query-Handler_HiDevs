# 🌐 Multilingual AI Translator Bot 🤖

A real-time AI assistant that detects, translates, and responds in multiple languages using Groq LLM.

---

## 🚀 Features

- 🌍 **Automatic Language Detection**  
  Detects user input language when "Auto Detect" is selected.

- 🔄 **Bidirectional Translation**  
  Translates queries to English for processing, then responds in the user’s chosen language.

- 💬 **Friendly AI Responses**  
  Generates helpful, clear, and concise replies tailored to the output language.

- 📝 **Conversation Logging**  
  Tracks interactions with timestamps, ratings, and translations for review or export.

- 📥 **Downloadable Logs**  
  Export your conversation history as a CSV file.

- 🖥️ **Interactive UI**  
  Built with Streamlit for easy use.

---

## 🛠️ Technologies Used

- Groq LLM (`llama-3.1-8b-instant`) via `langchain_groq`  
- Language detection with `langdetect`  
- Language name resolution via `langcodes`  
- Streamlit for the web UI  
- Pandas for data export  
- Environment variable management with `python-dotenv`  

---

## ⚙️ How It Works

1. 📝 User inputs query and selects input/output languages.  
2. 🔍 If input is set to Auto Detect, the bot detects the language automatically.  
3. 🔄 Query is translated into English if needed.  
4. 🤖 Groq LLM generates a reply in the specified output language.  
5. 💬 Translated reply and original text are displayed.  
6. ⭐ User can rate the response quality and optionally download logs.  

---

## 🏁 Getting Started

### Prerequisites

- Python 3.8+  
- Install dependencies:  
  ```bash
  pip install -r requirements.txt
  
---

## 🔗 Live Demo

Try it here : [Demo URL](https://real-time-multilingual-query-handlerhidevs-obwtgqtb4wqnikbxaxc.streamlit.app/)
