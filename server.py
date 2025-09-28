from flask import Flask, render_template, request, url_for, jsonify
from flask_socketio import SocketIO, emit
from gen import words2image
import random
import string
import time
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

socketio = SocketIO(app)

details = {}

def regen_image():
    for i in os.listdir("./static/image/temp"):
        os.remove("./static/image/temp/" + i)

    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    with open("words.txt", "r", encoding="utf8") as f:
        words = f.read().split()

    random.shuffle(words)

    image, positions, _, _ = words2image(words, fichier_sortie=f"./static/image/temp/{random_string}.png", largeur_max=800)

    return image, positions, url_for('static', filename=f'image/temp/{random_string}.png')

@app.route("/")
def home():
    _, pos, url = regen_image()
    return render_template("home.html", image_path=url, data_http=pos)

@app.route("/regen")
def regen():
    img, pos, url = regen_image()
    h, w = img.size
    return jsonify({
        "image": url, 
        "data": pos, 
        "image_w": w, 
        "image_h": h
    })

@socketio.on('session')
def session(sessionId):
    details[request.sid] = {
        "mots": 0, 
        "précision": 0, 
        "mots/min": 0, 
        "current_word": {
            "start_ts": 0, 
            "end_ts": 0, 
            "precision": 100, 
            "word": ""}, 
        "history": []
    }
    emit("detail", '... mots/min, ... mots tapés, ...% précision')

@socketio.on('message')
def handle_message(data:str):
    id = request.sid
    word, ts = data.split("|")
    ts = int(ts[:-3])

    if (time.time() - ts) > 5:
        print("[ERROR] Temps entre l'envoie et la reception trop long")
        return

    if word.endswith(" "):
        details[id]["current_word"]["end_ts"] = ts
        details[id]["history"].append(details[id]["current_word"])
        details[id]["current_word"] = {"start_ts": ts, "end_ts": 0, "word": ""}

        details[id]["mots"] = len(details[id]["history"])
        w1 = details[id]["history"][0]
        w2 = details[id]["history"][-1]
        try:
            details[id]["mots/min"] = round((60 * details[id]["mots"]) / (w2["end_ts"] - w1["start_ts"]))
        except: pass
        # details[id]["précision"] = TODO
    else:
        if details[id]["current_word"]["start_ts"] == 0:
            details[id]["current_word"]["start_ts"] = ts
        details[id]["current_word"]["word"] = word

    emit("detail", f'{details[id]["mots/min"]} mots/min, {details[id]["mots"]} mots tapés, {details[request.sid]["précision"]}% précision')

if __name__ == '__main__':
    print("[\033[94mINFO\033[0m] Host: \033[01m127.0.0.1\033[0m, Port: \033[01m5000\033[0m, URL: \033[01mhttp://127.0.0.1:5000/\033[0m")
    socketio.run(app, debug=False)
