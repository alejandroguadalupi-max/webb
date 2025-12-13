from flask import Flask, redirect, abort, request, jsonify, send_from_directory
import os

# Importamos las rutas y funciones
from generadorqr import create_qr, load_mapping, save_mapping, QR_DIR

app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor de QR dinámicos funcionando correctamente [OK]"

# 🔁 REDIRECCIÓN QR
@app.route("/r/<code>")
def redirect_code(code):
    mapping = load_mapping()
    if code in mapping:
        data = mapping[code]
        if isinstance(data, dict):
            url_destino = data.get("url")
        else:
            url_destino = data 
            
        if url_destino:
            print(f"Redirigiendo QR {code} -> {url_destino}")
            return redirect(url_destino, code=302)
            
    return abort(404, description="QR no encontrado")

# 🧩 CREAR QR
@app.route("/api/create_qr", methods=["POST"])
def api_create_qr():
    try:
        data = request.get_json()
        nombre = data.get("name")
        destino = data.get("url")

        if not nombre or not destino:
            return jsonify({"error": "Datos incompletos"}), 400

        result = create_qr(destino, nombre)
        return jsonify(result)
        
    except Exception as e:
        print(f"[ERROR CRITICO] Al crear QR: {e}")
        # Esto imprimirá el error real en la consola en vez de solo "500"
        return jsonify({"error": str(e)}), 500

# 🔄 ACTUALIZAR DESTINO
@app.route("/api/update", methods=["POST"])
def update_qr():
    try:
        data = request.get_json()
        code = data.get("code")
        new_url = data.get("url")

        if not code or not new_url:
            return jsonify({"error": "Datos incompletos"}), 400

        mapping = load_mapping()
        if code not in mapping:
            return jsonify({"error": "Código no existe"}), 404

        if isinstance(mapping[code], dict):
            mapping[code]["url"] = new_url
        else:
            mapping[code] = {"url": new_url, "name": "Desconocido"}
            
        save_mapping(mapping)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🖼️ SERVIR IMÁGENES QR (VERSIÓN BLINDADA)
@app.route("/QR/<filename>")
def serve_qr(filename):
    try:
        # 1. Asegurar ruta absoluta
        full_path = os.path.join(QR_DIR, filename)
        
        # 2. Verificar existencia
        if not os.path.exists(full_path):
            print(f"[ERROR] Archivo no encontrado fisicamente en: {full_path}")
            return abort(404)
            
        # 3. Enviar archivo
        print(f"[INFO] Enviando archivo: {filename}")
        return send_from_directory(QR_DIR, filename)
        
    except Exception as e:
        print(f"[ERROR CRITICO] Al enviar imagen {filename}: {e}")
        return abort(500, description=str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)