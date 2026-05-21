# Ultimate PoC — Double-Clickjacking (serverless)

Configurable proof of concept for Double-Clickjacking using a popunder window
and Flappy Bird to capture clicks. Deploys to Vercel as a serverless function.

**Read [The Ultimate Double-Clickjacking PoC](https://jorianwoltjer.com/blog/p/hacking/ultimate-doubleclickjacking-poc)
for the original research.**

## Quick Deploy

1. Fork this repo
2. Go to [Vercel](https://vercel.com) → Import → select your fork
3. Set environment variable `TARGET_URL` to your OAuth device URL:
   ```
   TARGET_URL=https://vercel.com/oauth/device?user_code=XXXX-XXXX
   ```
4. Deploy

## Configuration

| Variable | Description |
|---|---|
| `TARGET_URL` | OAuth device authorization URL (env var or edit `main.py`) |
| `POPUP_SIZE` | `[width, height]` — smallest size that shows the button |
| `BUTTON_OFFSET` | `{pos: [x,y], size: [w,h]}` — button position inside popup |
| `USE_HISTORY_BACK` | `False` = reload URL; `True` = `history.back()` |

### How to measure

Open the target URL as a popup, resize to minimum, then run in Console:

```js
// POPUP_SIZE
copy(JSON.stringify([window.outerWidth, window.outerHeight]))

// BUTTON_OFFSET — select button with Inspect Element first ($0)
copy((r=$0.getBoundingClientRect(), JSON.stringify({
    pos: [Math.floor(r.x), Math.floor(r.y)],
    size: [Math.floor(r.width), Math.floor(r.height)]
})))
```

## Local dev

```sh
pip install -r requirements.txt
python main.py
# → http://localhost:8000
```

## Architecture

```
/                        → fake Cloudflare captcha (popunder)
/game                    → Flappy Bird + popup manipulation
/api/index.py            → Vercel serverless entry point
vercel.json              → Vercel routing config
.github/workflows/       → CI/CD (auto-approve PRs)
```
