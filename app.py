from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'geheimcode'

DATA_FILE = "daten.txt"
CONFIG_FILE = "stockanzahl.txt"

def lade_reihen_konfiguration():
    reihen = {}
    with open(CONFIG_FILE, "r") as f:
        for line in f:
            if ":" in line:
                reihe, anzahl = line.strip().split(":")
                reihen[int(reihe)] = int(anzahl)
    return reihen

@app.route("/", methods=["GET", "POST"])
def start():
    reihen_config = lade_reihen_konfiguration()
    if request.method == "POST":
        reihe = int(request.form["reihe"])
        session["reihe"] = reihe
        session["stock"] = 1
        session["max_stock"] = reihen_config.get(reihe, 30)
        return redirect(url_for("bewerten"))
    return render_template("start.html", reihen=sorted(reihen_config.keys()))

@app.route("/bewerten", methods=["GET", "POST"])
def bewerten():
    if "reihe" not in session or "stock" not in session:
        return redirect(url_for("start"))

    reihe = session["reihe"]
    stock = session["stock"]
    max_stock = session["max_stock"]

    if request.method == "POST":
        bewertung = request.form["bewertung"]
        reihe = session["reihe"]
        stock = session["stock"]

        with open(DATA_FILE, "a") as f:
            f.write(f"Reihe {reihe}, Stock {stock}, Bewertung {bewertung}\n")

        if stock < session["max_stock"]:
            session["stock"] += 1
        else:
            session["reihe_fertig"] = reihe  # speichern für nächste Seite
            return redirect(url_for("fertig"))

        return redirect(url_for("bewerten"))  # <-- WICHTIG: Redirect statt direkt rendern


    return render_template("bewerten.html", reihe=reihe, stock=stock)

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("start"))

@app.route("/fertig")
def fertig():
    reihe = session.get("reihe_fertig", "?")
    return render_template("fertig.html", reihe=reihe)

from flask import send_file

@app.route("/download")
def download():
    return send_file("daten.txt", as_attachment=True)

@app.route("/reset-daten")
def reset_daten():
    with open("daten.txt", "w") as f:
        f.write("")  # Datei leeren
    return "daten.txt wurde geleert."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
