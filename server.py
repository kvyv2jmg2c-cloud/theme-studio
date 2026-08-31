import os
import requests

from flask import Flask, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


@app.route("/")
def home():
    return jsonify({
        "ok": True,
        "service": "Telegram Theme Studio",
        "status": "online"
    })


@app.route("/api/chat-id")
def get_chat_id():

    if not BOT_TOKEN:
        return jsonify({
            "ok": False,
            "error": "TELEGRAM_BOT_TOKEN не найден"
        })

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

    response = requests.get(url, timeout=30)

    return jsonify(response.json())


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )