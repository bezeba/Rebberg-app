from flask import Flask, render_template, request, redirect, url_for, session, send_file
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
                reinen[int(reihe)] = int(anzahl)
    return reihen

@app.route("/", methods=["GET", "POST"])
def start():
    reihen_config = lade_reihen_konfiguration()
    if request.method == "POST":
        reihe = int(request.form["reihe"])
        richtung = request.form["richtung"]
        session["reihe"] = reihe
        session["richtung"] = richtung

        max_stock = reihen_config.get(reihe, 30)
        session["max_stock"] = max_stock
        session["stock"] = 1 if richtung == "vor" else max_stock

        return redirect(url_for("bewerten"))

    return render_template("start.html", reihen=sorted(reihen_config.keys()))

@app.route("/bewerten", methods=["GET", "POST"])
def bewerten():
    if "reihe" not in session or "stock" not in session:
        return redirect(url_for("start"))

    reihe = session["reihe"]
    stock = session["stock"]
    richtung = session["richtung"]
    max_stock = session["max_stock"]

    if request.method == "POST":
        bewertung = request.form["bewertung"]
        with open(DATA_FILE, "a") as f:
            f.write(f"Reihe {reihe}, Stock {stock}, Bewertung {bewertung}\n")

        if richtung == "vor":
            if stock < max_stock:
                session["stock"] += 1
            else:
                session["reihe_fertig"] = reihe
                return redirect(url_for("fertig"))
        else:
            if stock > 1:
                session["stock"] -= 1
            else:
                session["reihe_fertig"] = reihe
                return redirect(url_for("fertig"))

        return redirect(url_for("bewerten"))

    return render_template("bewerten.html", reihe=reihe, stock=stock)

@app.route("/fertig")
def fertig():
    reihe = session.get("reihe_fertig", "?")
    return render_template("fertig.html", reihe=reihe)

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("start"))

@app.route("/download")
def download():
    return send_file(DATA_FILE, as_attachment=True)

@app.route("/reset-daten")
def reset_daten():
    with open(DATA_FILE, "w") as f:
        f.write("")
    return "daten.txt wurde geleert."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
