"""Re-render trigger.

The remodeller on the site posts a request here; this fires the GitHub workflow that
rebuilds the piece at those numbers, renders it and commits it back. The GitHub token
never leaves this service - the page holds nothing but the endpoint URL and a shared
key that only deters casual abuse.

  POST /render   {"piece":"hammer","way":"teal_silver","label":"...","dims":{...}}
  GET  /health
"""
import json, os, re, time

import requests
from flask import Flask, jsonify, request

REPO = os.environ.get("REPO", "zelidav/jbd-clearboy")
WORKFLOW = os.environ.get("WORKFLOW", "variant.yml")
REF = os.environ.get("REF", "main")
SHARED_KEY = os.environ.get("SHARED_KEY", "")
TOKEN = os.environ.get("GH_TOKEN", "").strip()   # secrets often carry a newline
ALLOWED_ORIGINS = ("https://zelidav.github.io", "https://claude.ai", "http://localhost")

PIECES = {"hammer", "jar"}
WAYS = {"teal_silver", "magenta_gold", "clear_silver", "clear_gold"}
DIMS = {"height", "headlen", "headsec", "stemod", "stemlen", "bowlid", "footod",
        "marbles", "scatter", "mouthid", "wall", "fritz", "corkh"}

app = Flask(__name__)
_recent = []                      # crude rate limit: 6 requests / 10 minutes


def cors(resp):
    origin = request.headers.get("Origin", "")
    if any(origin.startswith(a) for a in ALLOWED_ORIGINS):
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Headers"] = "content-type"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return resp


def clean(req):
    """Only the fields the renderer understands, in the ranges it can build."""
    piece = req.get("piece")
    way = req.get("way")
    if piece not in PIECES:
        raise ValueError("unknown piece %r" % piece)
    if way not in WAYS:
        raise ValueError("unknown colourway %r" % way)
    dims = {}
    for k, v in (req.get("dims") or {}).items():
        if k not in DIMS:
            raise ValueError("unknown dimension %r" % k)
        f = float(v)
        if not (0 < f <= 300):
            raise ValueError("%s out of range" % k)
        dims[k] = f
    label = re.sub(r"[^\w \-.]", "", str(req.get("label") or "variant"))[:40].strip()
    notes = str(req.get("notes") or "")[:1200]
    return {"piece": piece, "way": way, "label": label or "variant",
            "notes": notes, "dims": dims}


@app.route("/health")
def health():
    return jsonify(ok=True, repo=REPO, workflow=WORKFLOW, token=bool(TOKEN))


@app.route("/render", methods=["POST", "OPTIONS"])
def render():
    if request.method == "OPTIONS":
        return cors(app.make_response(("", 204)))
    if SHARED_KEY and request.headers.get("X-Render-Key") != SHARED_KEY:
        return cors(jsonify(error="bad key")), 403

    now = time.time()
    _recent[:] = [t for t in _recent if now - t < 600]
    if len(_recent) >= 6:
        return cors(jsonify(error="too many requests, try again in a few minutes")), 429

    try:
        spec = clean(request.get_json(force=True, silent=False) or {})
    except Exception as e:
        return cors(jsonify(error=str(e))), 400

    if not TOKEN:
        return cors(jsonify(error="service has no GitHub token configured")), 500

    try:
        r = requests.post(
            "https://api.github.com/repos/%s/actions/workflows/%s/dispatches"
            % (REPO, WORKFLOW),
            headers={"Authorization": "Bearer " + TOKEN,
                     "Accept": "application/vnd.github+json"},
            json={"ref": REF, "inputs": {"request": json.dumps(spec)}},
            timeout=20)
    except Exception as e:                      # never let a token reach the logs
        return cors(jsonify(error="could not reach github", detail=type(e).__name__)), 502
    if r.status_code != 204:
        return cors(jsonify(error="github said %s" % r.status_code,
                            detail=r.text[:400])), 502
    _recent.append(now)
    return cors(jsonify(ok=True, queued=spec,
                        actions="https://github.com/%s/actions" % REPO,
                        site="https://zelidav.github.io/jbd-clearboy/"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
