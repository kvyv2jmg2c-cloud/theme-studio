import os
import requests

from flask import Flask, jsonify, request

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


@app.route("/api/theme", methods=["POST"])
def create_theme():

    if not BOT_TOKEN:
        return jsonify({
            "ok": False,
            "error": "TELEGRAM_BOT_TOKEN не найден"
        }), 500

    try:
        data = request.get_json(force=True)

        name = data.get(
            "name",
            "Telegram Theme"
        )

        colors = data.get(
            "colors",
            {}
        )

        chat_id = data.get(
            "chat_id"
        )

        if not chat_id:
            return jsonify({
                "ok": False,
                "error": "CHAT_ID не указан"
            }), 400

        def get_color(key, default):

            value = colors.get(
                key,
                default
            )

            value = str(value)

            if value.startswith("#"):
                value = value[1:]

            try:
                return int(value, 16)
            except:
                return int(
                    default.replace("#", ""),
                    16
                )

        theme = f"""name: {name}

windowBackgroundWhite: {get_color("background", "#111114")}
actionBarDefault: {get_color("header", "#18181d")}
actionBarDefaultIcon: {get_color("text", "#ffffff")}
actionBarDefaultTitle: {get_color("text", "#ffffff")}

windowBackgroundWhiteBlackText: {get_color("text", "#ffffff")}
windowBackgroundWhiteGrayText: {get_color("secondary", "#9999a3")}
windowBackgroundWhiteLinkText: {get_color("link", "#ff4fa3")}

chat_outBubble: {get_color("outgoing", "#ff4fa3")}
chat_inBubble: {get_color("incoming", "#292930")}

chat_messageTextIn: {get_color("text", "#ffffff")}
chat_messageTextOut: {get_color("text", "#ffffff")}

chat_linkIn: {get_color("link", "#ff4fa3")}
chat_linkOut: {get_color("link", "#ff4fa3")}

chat_outSentCheck: {get_color("accent", "#ff4fa3")}
chat_inSentCheck: {get_color("accent", "#ff4fa3")}
"""

        filename = str(
            name
        ).strip()

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

        telegram_response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
            data={
                "chat_id": chat_id,
                "caption":
                    f"🎨 Тема «{name}» готова!"
            },
            files=files,
            timeout=30
        )

        return jsonify(
            telegram_response.json()
        )

    except Exception as e:

        return jsonify({
            "ok": False,
            "error": str(e)
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