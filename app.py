from flask import Flask, render_template, request, jsonify
from chatbot import chatbot_response  # Import your chatbot logic

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")  # Load the frontend

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    bot_reply = chatbot_response(user_input)
    return jsonify({"response": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)