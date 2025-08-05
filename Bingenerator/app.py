from flask import Flask, render_template, request, redirect, url_for, flash
import random
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave-secreta'

def generar_luhn(bin_format, mes, año, cantidad):
    tarjetas = []

    # Detectar longitud del CVV según tipo de tarjeta usando binlist
    cvv_largo = 3  # valor por defecto
    try:
        consulta_bin = bin_format.replace("x", "")[:6]
        if len(consulta_bin) >= 6:
            response = requests.get(f"https://lookup.binlist.net/{consulta_bin}")
            data = response.json()
            esquema = data.get("scheme", "").lower()
            if esquema == "amex":
                cvv_largo = 4
    except:
        pass  # si falla la conexión o la respuesta, usar CVV de 3 dígitos

    for _ in range(int(cantidad)):
        tarjeta = ''
        for char in bin_format:
            if char == 'x':
                tarjeta += str(random.randint(0, 9))
            else:
                tarjeta += char
        tarjeta += calcular_digito_luhn(tarjeta)

        # Mes aleatorio si se seleccionó "aleatorio"
        mes_final = mes if mes != "aleatorio" else str(random.randint(1, 12)).zfill(2)

        # Año aleatorio entre el año actual y 5 años más
        if año != "aleatorio":
            año_final = año
        else:
            año_actual = datetime.now().year
            año_final = str(random.randint(año_actual, año_actual + 5))[2:]  # últimos 2 dígitos

        # Generar CVV según la longitud determinada
        cvv = str(random.randint(0, 10**cvv_largo - 1)).zfill(cvv_largo)

        tarjetas.append(f"{tarjeta}|{mes_final}|{año_final}|{cvv}")
    return tarjetas

def calcular_digito_luhn(numero):
    total = 0
    reverse_digits = numero[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return str((10 - (total % 10)) % 10)

@app.route("/", methods=["GET", "POST"])
def index():
    tarjetas = []
    if request.method == "POST":
        bin_input = request.form["bin"].strip()
        mes = request.form["mes"]
        año = request.form["año"]
        cantidad = request.form["cantidad"]

        # Completar con 'x' si no se ingresaron
        if 'x' not in bin_input:
            bin_input = bin_input[:15]
            bin_input += 'x' * max(0, 15 - len(bin_input))

        tarjetas = generar_luhn(bin_input, mes, año, cantidad)
    return render_template("index.html", tarjetas=tarjetas)

@app.route("/guardar", methods=["POST"])
def guardar():
    tarjetas = request.form["tarjetas"]
    with open("BinGuardados.txt", "a", encoding="utf-8") as f:
        f.write(tarjetas + "\n")
    flash("✅ Tarjetas guardadas con éxito", "success")
    return redirect(url_for("index"))

@app.route("/ver_guardadas")
def ver_guardadas():
    try:
        with open("BinGuardados.txt", "r", encoding="utf-8") as f:
            contenido = f.read()
    except FileNotFoundError:
        contenido = "No hay tarjetas guardadas aún."
    return f"<pre>{contenido}</pre><br><a href='/'>🔙 Volver</a>"

@app.route("/bin_checker", methods=["POST"])
def bin_checker():
    bin_input = request.form.get("bin", "")
    if not bin_input or len(bin_input) < 6:
        flash("❌ BIN inválido o vacío", "danger")
        return redirect(url_for("index"))
    
    try:
        response = requests.get(f"https://lookup.binlist.net/{bin_input}")
        data = response.json()
        info = f"✅ BIN válido: {data.get('scheme','')} - {data.get('type','')} - {data.get('bank',{}).get('name','')}"
        flash(info, "success")
    except Exception:
        flash("❌ No se pudo verificar el BIN", "danger")
    return redirect(url_for("index"))

@app.route("/creditos")
def creditos():
    return "<h2>💡 CRÉDITOS💡</h2><p>PÁGINA WEB CREADA POR JESUS. DERECHOS DE AUTOR 2025.</p><a href='/'>🔙 Volver</a>"

@app.route("/info")
def info():
    return "<h2>ℹ️ INFORMACIÓN</h2><p>ESTE ES UN GENERADOR DE CC PARA SUSCRIPCIONES DE PRUEBAS GRATIS DE PLATAFORMAS DE STREAMING.</p><a href='/'>🔙 Volver</a>"

if __name__ == "__main__":
    app.run(debug=True)
