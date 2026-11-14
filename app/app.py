"""Aplicación web Flask de la calculadora."""

from flask import Flask, render_template, request

from .calculadora import dividir, multiplicar, restar, sumar

app = Flask(__name__)

OPERACIONES = {
    "sumar": sumar,
    "restar": restar,
    "multiplicar": multiplicar,
    "dividir": dividir,
}


@app.route("/", methods=["GET", "POST"])
def index():
    """Muestra el formulario y, en un POST, calcula el resultado."""
    resultado = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            operacion = OPERACIONES.get(request.form["operacion"])
            if operacion is None:
                resultado = "Operación no válida"
            else:
                resultado = operacion(num1, num2)
        except ValueError:
            resultado = "Error: Introduce números válidos"
        except ZeroDivisionError:
            resultado = "Error: No se puede dividir por cero"

    return render_template("index.html", resultado=resultado)


if __name__ == "__main__":  # pragma: no cover
    app.run(port=5000, host="0.0.0.0")
