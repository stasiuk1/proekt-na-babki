from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import json
import pathlib
import requests
from dotenv import dotenv_values  # ← эта строка должна быть
# Загрузка конфигурации из .env
config = dotenv_values(".env")
GA_ID = config.get("GA_TRACKING_ID")
ADSENSE_ID = config.get("ADSENSE_PUB_ID")
TG_TOKEN = config.get("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = config.get("TELEGRAM_CHAT_ID")

app = Flask(__name__)

DATA_PATH = pathlib.Path("data")
SITES_PATH = pathlib.Path("sites")
UPLOAD_PATH = pathlib.Path("static/uploads")
EARNINGS_FILE = DATA_PATH / "earnings.json"

def send_telegram(text):
    if TG_TOKEN and TG_CHAT_ID:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_CHAT_ID, "text": text}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print("Telegram error:", e)

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/api/sites')
def api_sites():
    with open(EARNINGS_FILE, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

@app.route('/api/create', methods=['POST'])
def api_create():
    niche = request.json['niche']
    site_name = ''.join(filter(str.isalnum, niche.title().replace(" ", "")))
    site_dir = SITES_PATH / site_name
    site_dir.mkdir(parents=True, exist_ok=True)

    for i in range(3):
        article = f"<html><head><title>{niche} #{i+1}</title>"
        article += f"<script async src='https://www.googletagmanager.com/gtag/js?id={GA_ID}'></script><script>window.dataLayer = window.dataLayer || []; function gtag(){{dataLayer.push(arguments);}} gtag('js', new Date()); gtag('config', '{GA_ID}');</script>"
        article += f"</head><body><h1>{niche} #{i+1}</h1><p>AI content for {niche}</p><br><div class='ad'>AdSense block for {ADSENSE_ID}</div><script>/* ads would go here */</script></body></html>"
        with open(site_dir / f"page-{i+1}.html", "w", encoding="utf-8") as f:
            f.write(article)

    with open(EARNINGS_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data[site_name] = {"adsense": 0, "affiliate": 0, "sales": 0}
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    send_telegram(f"📢 Новый сайт создан: {site_name}")
    return jsonify({"status": "created", "site": site_name})

@app.route("/edit/<site>/<page>", methods=["GET", "POST"])
def edit_page(site, page):
    path = SITES_PATH / site / page
    if request.method == "POST":
        with open(path, "w", encoding="utf-8") as f:
            f.write(request.form["content"])
        send_telegram(f"✏️ Изменена страница: {site}/{page}")
        return redirect("/dashboard")
    with open(path, "r", encoding="utf-8") as f:
        return render_template("editor.html", site_name=site, content=f.read())

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        f = request.files["file"]
        f.save(UPLOAD_PATH / f.filename)
        send_telegram(f"📎 Загружен файл: {f.filename}")
        return f"Загружено: {f.filename}"
    return render_template("upload.html")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_PATH, filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)