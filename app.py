from flask import Flask, request, jsonify, render_template
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, ToolMessage
from langchain.tools import tool
from PIL import Image
import base64
import io
import os

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Tool ──────────────────────────────────────────────────────────────────────

@tool
def food_name_register(food_name: str) -> str:
    """Registers a food name in the system."""
    return f"Food name '{food_name}' has been registered successfully."

# ── LLM setup ─────────────────────────────────────────────────────────────────

llm = ChatGroq(model="meta-llama/Llama-4-scout-17b-16e-instruct", temperature=0.5)
llm_with_tool = llm.bind_tools([food_name_register])

# ── Helpers ───────────────────────────────────────────────────────────────────

def image_to_base64(image_path: str, max_pixels: int = 3_000_000) -> str:
    with Image.open(image_path) as img:
        w, h = img.size
        if w * h > max_pixels:
            scale = (max_pixels / (w * h)) ** 0.5
            img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        if img.mode != "RGB":
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")


def run_food_agent(user_text: str = None, image_path: str = None) -> str:
    content = []
    if user_text:
        content.append({"type": "text", "text": user_text})
    else:
        content.append({"type": "text", "text": "Identify the food item in the image and provide its recipe."})

    if image_path:
        b64 = image_to_base64(image_path)
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})

    messages = [HumanMessage(content=content)]
    ai_msg = llm_with_tool.invoke(messages)
    messages.append(ai_msg)

    food_name = None
    if ai_msg.tool_calls:
        for call in ai_msg.tool_calls:
            if call["name"] == "food_name_register":
                food_name = call["args"]["food_name"]
                tool_response = food_name_register.invoke(call["args"])
                messages.append(ToolMessage(content=tool_response, tool_call_id=call["id"]))
        response = llm_with_tool.invoke(messages)
        header = f"🍽️ **{food_name}**\n\n" if food_name else ""
        return header + response.content

    return ai_msg.content

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_text = request.form.get("message", "").strip() or None
    image_file = request.files.get("image")
    image_path = None

    if image_file and image_file.filename:
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_file.filename)
        image_file.save(save_path)
        image_path = save_path

    if not user_text and not image_path:
        return jsonify({"error": "Please send a message or an image."}), 400

    try:
        reply = run_food_agent(user_text=user_text, image_path=image_path)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
