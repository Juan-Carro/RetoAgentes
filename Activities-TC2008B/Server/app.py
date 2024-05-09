from flask import Flask, jsonify
from json import load
import sys

app = Flask(__name__)

@app.route("/", methods=['GET'])
def main() -> str:
    return "<p>Hello, World!</p>"

# ------------------------------------

# TODO: Checar funcionalidad
@app.route("/obtain_cars", methods=['GET'])
def obtain_cars():
    try:
        with open('obtain_cars.json', 'r') as file:
            data = load(file)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': 'hay un error'})

# Falta esta implementacion, primero va coche
@app.route("/obtain_semaforos", methods=['GET'])
def obtain_semaforos():
    try:
        with open('obtain_state_semaforos.json', 'r') as file:
            data = load(file)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': 'hay un error'})


if __name__ == '__main__':
    app.run(debug=True)