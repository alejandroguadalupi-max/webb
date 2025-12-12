import os
import json
import re
import uuid
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image

MAPPING_FILE = "mapping.json"
SALIDA = "QR"
LOGO_FILE = "logo.png"

BASE_URL = "https://webb-production-7e89.up.railway.app/r"

def slugify(s):
    return re.sub(r'[\\/*?:"<>| ]+', "", s)

def load_mapping():
    if not os.path.exists(MAPPING_FILE):
        return {}
    try:
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_mapping(mapping):
    try:
        with open(MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def generate_id():
    return uuid.uuid4().hex[:8]

def create_qr(destino, nombre, logo_path=None):
    os.makedirs(SALIDA, exist_ok=True)

    mapping = load_mapping()

    new_id = generate_id()
    mapping[new_id] = destino

    save_mapping(mapping)

    qr_url = f"{BASE_URL}/{new_id}"

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        w, h = img.size
        logo_size = int(w * 0.25)
        logo.thumbnail((logo_size, logo_size))
        pos = ((w - logo.width) // 2, (h - logo.height) // 2)
        img.paste(logo, pos, mask=logo)

    out_path = os.path.join(SALIDA, f"{slugify(nombre)}.png")
    img.save(out_path)

    return new_id, qr_url, out_path

if __name__ == "__main__":
    destino = input("URL destino real: ").strip()
    nombre = input("Nombre archivo QR: ").strip()
    logo = LOGO_FILE if os.path.exists(LOGO_FILE) else None

    new_id, qr_url, path = create_qr(destino, nombre, logo)
    print("ID generado:", new_id)
    print("URL dentro del QR:", qr_url)
    print("Archivo guardado en:", path)
