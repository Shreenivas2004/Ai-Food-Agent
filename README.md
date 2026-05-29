# 🍜 FoodBot — AI Recipe Assistant

A Flask chatbot that wraps your multi-model food agent, supporting both text queries and image uploads.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Groq API key
export GROQ_API_KEY="your-groq-api-key-here"

# 3. Run the app
python app.py
```

Then open **http://localhost:5000** in your browser.

## Features

- 💬 **Text chat** — ask for any recipe by name
- 📷 **Image upload** — drop a food photo to identify it + get its recipe
- 🔧 **Tool use** — registers identified food names via LangChain tool
- 🎨 **Dark UI** — clean chat interface with typing indicator

## Project Structure

```
food_agent_app/
├── app.py               # Flask app + food agent logic
├── requirements.txt
├── templates/
│   └── index.html       # Chat UI
└── static/
    └── uploads/         # Temp image storage
```
