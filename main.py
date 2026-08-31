import os
import uuid
import requests
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
# Папка для созданных тем
THEMES_DIR = "/tmp/themes"
os.makedirs(THEMES_DIR, exist_ok=True)
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
@app.route("/theme/<theme_id>")
def download_theme(theme_id):
    # Защита от попытки указать путь к другому файлу
    if "/" in theme_id or "\\" in theme_id or ".." in theme_id:
        return "Invalid theme", 400
    filepath = os.path.join(
        THEMES_DIR,
        theme_id + ".attheme"
    )
    if not os.path.exists(filepath):
        return "Тема не найдена или срок её хранения истёк.", 404
    return send_file(
        filepath,
        as_attachment=True,
        download_name=theme_id + ".attheme",
        mimetype="application/octet-stream"
    )
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
                return int(
                    value,
                    16
                )
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
windowBackgroundWhiteLinkText: {color("link", "#7180FF")}
chat_outBubble: {color("outgoing", "#7180FF")}
chat_inBubble: {color("incoming", "#292930")}
chat_messageTextIn: {color("text", "#FFFFFF")}
chat_messageTextOut: {color("text", "#FFFFFF")}
chat_linkIn: {color("link", "#7180FF")}
chat_linkOut: {color("link", "#7180FF")}
chat_outSentCheck: {color("accent", "#7180FF")}
chat_inSentCheck: {color("accent", "#7180FF")}
"""
        # Безопасное имя файла
        clean_name = str(name).strip()
        if not clean_name:
            clean_name = "Telegram_Theme"
        clean_name = clean_name.replace(
            " ",
            "_"
        )
        clean_name = clean_name.replace(
            "/",
            "_"
        )
        clean_name = clean_name.replace(
            "\\",
            "_"
        )
        # Уникальный ID темы
        theme_id = (
            clean_name[:40]
            + "_"
            + uuid.uuid4().hex[:8]
        )
        filepath = os.path.join(
            THEMES_DIR,
            theme_id + ".attheme"
        )
        # Сохраняем тему
        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(theme)
        # Получаем публичный адрес Railway
        railway_url = os.environ.get(
            "RAILWAY_PUBLIC_DOMAIN"
        )
        if railway_url:
            if not railway_url.startswith("http"):
                railway_url = (
                    "https://"
                    + railway_url
                )
        else:
            railway_url = (
                request.host_url
                .rstrip("/")
            )
        download_url = (
            railway_url
            + "/theme/"
            + theme_id
        )
        # Кнопка в Telegram
        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": "⬇️ Скачать тему",
                        "url": download_url
                    }
                ]
            ]
        }
        caption = (
            f"🎨 Тема «{name}» готова!\n\n"
            f"Платформа: {platform}\n\n"
            f"Нажми кнопку ниже, чтобы скачать тему."
        )
        telegram = requests.post(
            f"https://api.telegram.org/"
            f"bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": caption,
                "reply_markup": keyboard
            },
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
                "Тема создана",
            "download_url":
                download_url,
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