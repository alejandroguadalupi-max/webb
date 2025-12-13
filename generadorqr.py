import os
import json
import re
import uuid
import socket
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image

# =========================
# CONFIGURACIÓN
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAPPING_FILE = os.path.join(BASE_DIR, "mapping.json")
QR_DIR = os.path.join(BASE_DIR, "QR")
LOGO_FILE = os.path.join(BASE_DIR, "logo.png")

# --- SELECCIÓN DE URL BASE ---
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

HOST_IP = get_local_ip() 
BASE_URL = "https://webb-production-7e89.up.railway.app/r"

# =========================
# UTILIDADES
# =========================

def slugify(text):
    """Limpia el nombre para usarlo como archivo"""
    clean = re.sub(r'[\\/*?:"<>| ]+', "_", text)
    return clean

def load_mapping():
    if not os.path.exists(MAPPING_FILE):
        return {}
    try:
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        # HE QUITADO EL EMOJI DE AQUI
        print(f"[AVISO] Error cargando mapping.json (se creara uno nuevo): {e}")
        return {}

def save_mapping(mapping):
    try:
        with open(MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=4, ensure_ascii=False)
    except Exception as e:
        # HE QUITADO EL EMOJI DE AQUI
        print(f"[ERROR] Error guardando mapping.json: {e}")

def generate_id():
    return uuid.uuid4().hex[:8]

# =========================
# FUNCIÓN PRINCIPAL
# =========================

def create_qr(destino, nombre, logo_path=LOGO_FILE):
    
    # 1. Asegurar carpeta QR
    os.makedirs(QR_DIR, exist_ok=True)

    # 2. Cargar mapping existente
    mapping = load_mapping()

    # 3. Generar ID único
    qr_id = generate_id()

    # 4. Guardar en JSON
    mapping[qr_id] = {
        "url": destino,
        "name": nombre
    }
    save_mapping(mapping)

    # 5. URL Intermedia
    qr_redirect_url = f"{BASE_URL}/{qr_id}"

    # 6. Generar QR
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_redirect_url)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGBA")

    # 7. Añadir logo
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            w, h = img.size
            logo_size = int(w * 0.25)
            logo.thumbnail((logo_size, logo_size))
            pos = ((w - logo.width) // 2, (h - logo.height) // 2)
            img.paste(logo, pos, mask=logo)
        except Exception as e:
            print(f"[AVISO] No se pudo anadir el logo: {e}")

    # 8. Guardar imagen
    filename = f"{slugify(nombre)}_{qr_id}.png"
    output_path = os.path.join(QR_DIR, filename)

    img.save(output_path)
    
    # HE QUITADO EL EMOJI DE AQUI (ESTE ERA EL CULPABLE PRINCIPAL)
    print(f"[OK] QR generado correctamente: {output_path}")

    return {
        "id": qr_id,
        "qr_url": qr_redirect_url,
        "image": filename,
        "status": "success"
    }

if __name__ == "__main__":
    print(f"URL Base actual: {BASE_URL}")
    r = create_qr("https://google.com", "Restaurante Prueba")
    print("Resultado:", r)