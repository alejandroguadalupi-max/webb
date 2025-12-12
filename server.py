from flask import Flask, redirect, abort
import json
import os

MAPPING_FILE = "mapping.json"

app = Flask(__name__)

def load_mapping():
    if not os.path.exists(MAPPING_FILE):
        return {}
    try:
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

@app.route("/r/<code>")
def redirect_code(code):
    mapping = load_mapping()
    if code in mapping:
        return redirect(mapping[code], code=302)
    return abort(404)

@app.route("/")
def home():
    return "Servidor de QR dinámicos funcionando correctamente 👍"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
