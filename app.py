from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import requests

app = Flask(__name__)
ips_capturadas = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/capturar-ip", methods=["GET", "POST"])
def capturar_ip():
    ip_cliente = request.remote_addr

    if request.headers.get("X-Forwarded-For"):
        ip_cliente = request.headers.get("X-Forwarded-For").split(",")[0].strip()

    info = {
        "IP": ip_cliente,
        "User-Agent": request.headers.get("User-Agent"),
        "Host": request.headers.get("Host"),
        "Accept-Language": request.headers.get("Accept-Language"),
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Referer": request.headers.get("Referer"),
    }

    try:
        geo = requests.get(
            f"http://ip-api.com/json/{ip_cliente}?fields=country,city,isp,org,lat,lon",
            timeout=5
        ).json()
        info.update({
            "País": geo.get("country"),
            "Ciudad": geo.get("city"),
            "ISP": geo.get("isp"),
            "Proveedor": geo.get("org"),
            "Coordenadas": f"{geo.get('lat')}, {geo.get('lon')}"
        })
    except Exception:
        pass

    ips_capturadas.append(info)

    with open("ips.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(info, ensure_ascii=False, indent=2) + "\n" + "=" * 80 + "\n")

    print(f"[CAPTURADA] IP: {ip_cliente} | Timestamp: {info['Timestamp']}")
    return jsonify(info)

@app.route("/ips-list")
def ips_list():
    return jsonify(ips_capturadas)

@app.route("/ver-ips")
def ver_ips():
    try:
        with open("ips.log", "r", encoding="utf-8") as f:
            contenido = f.read()
    except FileNotFoundError:
        contenido = "No hay IPs capturadas aún"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>IPs Capturadas</title>
        <style>
            body {{ font-family: Arial; background: #121212; color: white; padding: 20px; }}
            pre {{ background: #1d1d1d; padding: 20px; border-radius: 10px; overflow:auto; }}
        </style>
    </head>
    <body>
        <h1>IPs Capturadas</h1>
        <p>Total: <strong>{len(ips_capturadas)}</strong></p>
        <pre>{contenido}</pre>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
