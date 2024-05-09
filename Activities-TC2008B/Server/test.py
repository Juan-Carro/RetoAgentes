#!/usr/bin/python3

from flask import Flask
import json

app = Flask(__name__)

class Vector3():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Agent():
    def __init__(self, position, rotation):
        self.position = position
        self.rotation = rotation

class SimulationData():
    def __init__(self, count):
        self.agents = [Agent(Vector3(0, 0, 0), Vector3(0, 0, 0)) for i in range(count)]

    def count(self):
        return len(self.agent)

simulation_data = SimulationData(10)

@app.route("/")
# Para comunicación con servidores
#@app.get # Obtiene info del servidor
#@app.post # Enviar/guardar info al servidor
def hello_world():
    return "<p>Hello, World!</p>"

@app.get("/get-simulation-info")

def get_simulation_info():
    return "{Agent_count =" + str(simulation_data.count) + "}s"

@app.get("/get-agents-data")
def get_agents_data():
    return json.dumps(simulation_data)