import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
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
        }), 500
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
            timeout=30
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500
@app.route("/api/theme", methods=["POST", "OPTIONS"])
def create_theme():
    if request.method == "OPTIONS":
        return "", 200
    if not BOT_TOKEN:
        return jsonify({
            "ok": False,
            "error": "TELEGRAM_BOT_TOKEN не найден"
        }), 500
    if not CHAT_ID:
        return jsonify({
            "ok": False,
            "error": "TELEGRAM_CHAT_ID не найден"
        }), 500
    try:
        data = request.get_json(force=True) or {}
        name = data.get(
            "name",
            "Telegram Theme"
        )
        platform = data.get(
            "platform",
            "android"
        )
        colors = data.get(
            "colors",
            {}
        )
        def color(key, default):
            value = str(
                colors.get(
                    key,
                    default
                )
            )
            if value.startswith("#"):
                value = value[1:]
            try:
                return int(value, 16)
            except ValueError:
                return int(
                    default.replace("#", ""),
                    16
                )
        theme = f"""name: {name}
windowBackgroundWhite: {color("background", "#111114")}
actionBarDefault: {color("header", "#18181D")}
actionBarDefaultIcon: {color("text", "#FFFFFF")}
actionBarDefaultTitle: {color("text", "#FFFFFF")}
windowBackgroundWhiteBlackText: {color("text", "#FFFFFF")}
windowBackgroundWhiteGrayText: {color("secondary", "#999999")}
windowBackgroundWhiteLinkText: {color("link", "#FF4FA3")}
chat_outBubble: {color("outgoing", "#FF4FA3")}
chat_inBubble: {color("incoming", "#292930")}
chat_messageTextIn: {color("text", "#FFFFFF")}
chat_messageTextOut: {color("text", "#FFFFFF")}
chat_linkIn: {color("link", "#FF4FA3")}
chat_linkOut: {color("link", "#FF4FA3")}
chat_outSentCheck: {color("accent", "#FF4FA3")}
chat_inSentCheck: {color("accent", "#FF4FA3")}
"""
        filename = str(name).strip()
        if not filename:
            filename = "Telegram_Theme"
        filename = filename.replace(
            " ",
            "_"
        )
        filename = filename.replace(
            "/",
            "_"
        )
        filename = filename.replace(
            "\\",
            "_"
        )
        if not filename.endswith(".attheme"):
            filename += ".attheme"
        files = {
            "document": (
                filename,
                theme.encode("utf-8"),
                "application/octet-stream"
            )
        }
        caption = (
            f"🎨 Тема «{name}» готова!\n"
            f"Платформа: {platform}"
        )
        telegram = requests.post(
            f"https://api.telegram.org/"
            f"bot{BOT_TOKEN}/sendDocument",
            data={
                "chat_id": CHAT_ID,
                "caption": caption
            },
            files=files,
            timeout=30
        )
        result = telegram.json()
        if not telegram.ok:
            return jsonify({
                "ok": False,
                "telegram_error": result
            }), 500
        return jsonify({
            "ok": True,
            "message":
                "Тема отправлена в Telegram",
            "telegram":
                result
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "error":
                str(e)
        }), 500
if __name__ == "__main__":
    port = int(
        os.environ.get(
            "PORT",
            "8000"
        )
    )
    app.run(
        host="0.0.0.0",
        port=port
    )