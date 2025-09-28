import random
import string
from flask import Flask, render_template, url_for, jsonify
from gen import words2image
import os

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(debug=True)
