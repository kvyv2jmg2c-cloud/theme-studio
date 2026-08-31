import os
import io
import requests

from flask import Flask, request, jsonify

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
def chat_id():

    if not BOT_TOKEN:
        return jsonify({
            "ok": False,
            "error": "BOT TOKEN NOT FOUND"
        }), 500

    response = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
        timeout=20
    )

    return jsonify(response.json())


@app.route("/api/theme", methods=["POST"])
def create_theme():

    if not BOT_TOKEN:
        return jsonify({
            "ok": False,
            "error": "BOT TOKEN NOT FOUND"
        }), 500

    data = request.get_json(force=True)

    name = data.get("name", "Telegram Theme")

    colors = data.get("colors", {})

    def color(name, default):
        value = colors.get(name, default)
        return value.replace("#", "")

    theme = f"""name: {name}

windowBackgroundWhite: {int(color("background", "#111114"), 16)}
actionBarDefault: {int(color("header", "#18181d"), 16)}
actionBarDefaultIcon: {int(color("text", "#ffffff"), 16)}
actionBarDefaultTitle: {int(color("text", "#ffffff"), 16)}

windowBackgroundWhiteBlackText: {int(color("text", "#ffffff"), 16)}
windowBackgroundWhiteGrayText: {int(color("secondary", "#9999a3"), 16)}
windowBackgroundWhiteLinkText: {int(color("link", "#ff4fa3"), 16)}

chat_outBubble: {int(color("outgoing", "#ff4fa3"), 16)}
chat_inBubble: {int(color("incoming", "#292930"), 16)}

chat_messageTextIn: {int(color("text", "#ffffff"), 16)}
chat_messageTextOut: {int(color("text", "#ffffff"), 16)}

chat_linkIn: {int(color("link", "#ff4fa3"), 16)}
chat_linkOut: {int(color("link", "#ff4fa3"), 16)}

chat_outSentCheck: {int(color("accent", "#ff4fa3"), 16)}
chat_inSentCheck: {int(color("accent", "#ff4fa3"), 16)}
"""

    filename = name.strip()

    if not filename:
        filename = "Telegram_Theme"

    filename = filename.replace("/", "_")
    filename = filename.replace("\\", "_")
    filename = filename.replace(" ", "_")

    filename += ".attheme"

    files = {
        "document": (
            filename,
            io.BytesIO(theme.encode("utf-8")),
            "application/octet-stream"
        )
    }

    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
        data={
            "chat_id": data.get("chat_id"),
            "caption": f"🎨 Тема «{name}» готова!"
        },
        files=files,
        timeout=30
    )

    result = response.json()

    return jsonify(result)


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            8080
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )