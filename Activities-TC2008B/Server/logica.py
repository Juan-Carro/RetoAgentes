#!/usr/bin/python3
#type: ignore

from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import random
import heapq
import json
# from queue import PriorityQueue


# Agente para un edificio
class Building(Agent):
    def __init__(self, unique_id, model, color, number=None, is_semaforo=False, state="", direction=None,
                 cycle_length=5, initial_delay=0):
        super().__init__(unique_id, model)
        self.color = color
        self.number = number
        self.initial_color = color
        self.is_semaforo = is_semaforo
        self.state = state
        self.direction = direction
        if is_semaforo:
            self.cycle_counter = initial_delay
            self.cycle_length = cycle_length
            self.time_counter = 0

    def step(self):
        pass


# TODO: Aqui se hacen las direcciones
class RoadSign(Agent):
    def __init__(self, unique_id, model, direction, color="#000000"):
        super().__init__(unique_id, model)
        self.direction = direction  # 'N', 'S', 'E', 'W', 'NW', 'NE', 'SW', 'SE'
        self.color = color

    def directions(self, car):
        if self.direction == 'N':
            car.move_towards(0, 1)
        elif self.direction == 'S':
            car.move_towards(0, -1)
        elif self.direction == 'E':
            car.move_towards(1, 0)
        elif self.direction == 'W':
            car.move_towards(-1, 0)
        elif self.direction == 'NW':
            car.move_towards(-1, 1)
        elif self.direction == 'NE':
            car.move_towards(1, 1)
        elif self.direction == 'SW':
            car.move_towards(-1, -1)
        elif self.direction == 'SE':
            car.move_towards(1, -1)

    def step(self):
        pass



# Modelo con multiples edificios, estacionamientos, etc.
class CityModel(Model):
    def __init__(self, width, height, buildings_info, specials_info, semaforos_info, directions_info):
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.parking_spots = [(info['x'], info['y']) for info in specials_info] #Especificar la dirección
        self.edificios = [(info2['x'], info2['y'], info2['width'], info2['height']) for info2 in buildings_info]

        building_id_counter = 1


        # Lista de puntos en la carretera
        self.road_points = []
        for direction_info in directions_info:
            for x in range(direction_info['x'], direction_info['x'] + direction_info['width']):
                for y in range(direction_info['y'], direction_info['y'] + direction_info['height']):
                    cell_contents = self.grid.get_cell_list_contents((x, y))
                    if not cell_contents or not any(isinstance(obj, Building) for obj in cell_contents):
                        self.road_points.append((x, y))

        # Add buildings to the grid
        for building_info in buildings_info:
            for dx in range(building_info['x'], building_info['x'] + building_info['width']):
                for dy in range(building_info['y'], building_info['y'] + building_info['height']):
                    building = Building(building_id_counter, self, building_info['color'])
                    self.grid.place_agent(building, (dx, dy))
                    self.schedule.add(building)
                    building_id_counter += 1

        # Add special squares to the grid Aqui se agrega direction
        for special_info in specials_info:
            special_square = Building(building_id_counter, self, special_info['color'], special_info.get('number'))
            self.grid.place_agent(special_square, (special_info['x'], special_info['y']))
            self.schedule.add(special_square)
            building_id_counter += 1

        # Agregar vehículos
        num_cars = 200
        for _ in range(num_cars):
            start_position = random.choice(self.road_points)  # Elegir un punto de inicio en la carretera
            end_position = random.choice(self.parking_spots)  # Elegir un punto de fin en los estacionamientos
            car = Car(building_id_counter, self, start_position, end_position)
            self.grid.place_agent(car, start_position)
            self.schedule.add(car)
            building_id_counter += 1

        # Añadir direcciones a la cuadrícula
        for direction_info in directions_info:
            for dx in range(direction_info['width']):
                for dy in range(direction_info['height']):
                    direction_sign = RoadSign(building_id_counter, self, direction_info['direction'],
                                              color=direction_info['color'])
                    self.grid.place_agent(direction_sign, (direction_info['x'] + dx, direction_info['y'] + dy))
                    self.schedule.add(direction_sign)
                    building_id_counter += 1

        for semaforo_info in semaforos_info:
            for dx in range(semaforo_info['width']):
                for dy in range(semaforo_info['height']):
                    initial_color = semaforo_info['color']
                    initial_state = 'green' if initial_color == '#00FF00' else 'red'
                    semaforo = Building(building_id_counter, self, initial_color, is_semaforo=True, state=initial_state,
                                        cycle_length=10)
                    self.grid.place_agent(semaforo, (semaforo_info['x'] + dx, semaforo_info['y'] + dy))
                    self.schedule.add(semaforo)
                    building_id_counter += 1

    def get_building_edges(self):
        """ Devuelve una lista de posiciones que son las orillas de los edificios. """
        edges = []
        for building in self.edificios:
            x, y, width, height = building
            # Agregar los bordes superior e inferior
            for dx in range(x, x + width):
                upper_edge = (dx, y - 1)
                lower_edge = (dx, y + height)
                if self.is_valid_edge(upper_edge): edges.append(upper_edge)
                if self.is_valid_edge(lower_edge): edges.append(lower_edge)
            # Agregar los bordes laterales
            for dy in range(y, y + height):
                left_edge = (x - 1, dy)
                right_edge = (x + width, dy)
                if self.is_valid_edge(left_edge): edges.append(left_edge)
                if self.is_valid_edge(right_edge): edges.append(right_edge)
        return edges

    def is_valid_edge(self, pos):
        """ Verifica si una posición es una orilla válida. """
        return self.on_grid(pos) and not self.is_road(pos)

    def is_road(self, pos):
        """ Verifica si una posición es parte de la carretera. """
        cell_contents = self.grid.get_cell_list_contents(pos)
        return any(isinstance(obj, RoadSign) for obj in cell_contents)  # Asumiendo que RoadSign se usa para marcar carreteras

    def on_grid(self, pos):
        """ Verifica si una posición está dentro del grid. """
        x, y = pos
        return 0 <= x < self.grid.width and 0 <= y < self.grid.height
    
    def update_vehicles(self):
        cars = [agent for agent in self.schedule.agents if isinstance(agent, Car)]
        if len(cars) <= 10:
            for car in cars:
                car.end_position = car.choose_new_destination()
                car.path = car.calculate_path(car.position, car.end_position)


    def step(self):
        self.update_semaforos()  # Actualizar el estado de los semáforos basándose en el tráfico
        self.schedule.step()  # Avanzar un paso en todos los agentes
        self.json_car_positions()  # Actualizar el formato JSON en tiempo real
        self.json_state_semaforo()  # Actualizar el formato JSON del estado del semaforo en tiempo real
        self.update_vehicles()

    def update_semaforos(self):
        for agent in self.schedule.agents:
            if isinstance(agent, Building) and agent.is_semaforo:
                # Incrementar el contador de tiempo del semáforo
                agent.time_counter += 1

                # Calcular la densidad de tráfico cerca del semáforo
                traffic_density = self.calculate_traffic_density_near_semaforo(agent)

                # Cambiar el estado del semáforo si es necesario
                if self.should_semaforo_change(agent, traffic_density):
                    self.change_semaforo_state(agent)

    def calculate_traffic_density_near_semaforo(self, semaforo):
        radius = 1  # Distancia de monitoreo
        traffic_count = 0

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                pos_to_check = (semaforo.pos[0] + dx, semaforo.pos[1] + dy)
                if self.on_grid(pos_to_check):
                    cell_contents = self.grid.get_cell_list_contents(pos_to_check)
                    traffic_count += sum(isinstance(obj, RoadSign) for obj in cell_contents)

        return traffic_count

    def should_semaforo_change(self, semaforo, traffic_count):
        min_duration = 5  # Tiempo mínimo que el semáforo debe permanecer en su estado actual
        traffic_threshold = 0  # Umbral de tráfico para cambiar el semáforo

        if semaforo.time_counter < min_duration:
            return False

        if semaforo.state == 'red' and traffic_count > traffic_threshold:
            return True  # Cambiar a verde si hay vehículos cerca

        if semaforo.state == 'green' and traffic_count <= traffic_threshold:
            return True  # Cambiar a rojo si no hay vehículos cerca

        return True

    def change_semaforo_state(self, semaforo):
        # Verificar si hay vehículos cerca del semáforo
        if self.are_vehicles_near(semaforo):
            if semaforo.state == 'red':  # Cambiar a verde solo si está en rojo
                semaforo.state = 'green'
                semaforo.color = '#00FF00'  # Verde
        else:
            if semaforo.state == 'green':  # Cambiar a rojo solo si está en verde
                semaforo.state = 'red'
                semaforo.color = '#FF0000'  # Rojo

        semaforo.time_counter = 0  # Reiniciar el contador de tiempo

    def are_vehicles_near(self, semaforo):
        # Define un radio de detección alrededor del semáforo
        detection_radius = 5
        for dx in range(-detection_radius, detection_radius + 1):
            for dy in range(-detection_radius, detection_radius + 1):
                pos_to_check = (semaforo.pos[0] + dx, semaforo.pos[1] + dy)
                if self.on_grid(pos_to_check):
                    cell_contents = self.grid.get_cell_list_contents(pos_to_check)
                    if any(isinstance(obj, Car) for obj in cell_contents):
                        return True
        return False


    # TODO: Checar la posicion del coche
    # FIXME 1: Ajustar la posicion con Unity
    def json_car_positions(self):
        print("Generando posiciones de coches para JSON.")  # Mensaje Debug
        car_positions = []
        for agent in self.schedule.agents:
            if isinstance(agent, Car):
                current = agent.obtain_position()
                direction = agent.obtain_direction()

                car_data = {
                    "id": agent.unique_id,  # ID del agente coche
                    "position": current,  # Obtener la posición en formato de diccionario
                    "direction": direction  # Obtener la dirección en formato de cadena de texto
                }
                car_positions.append(car_data)

        try:
            with open('obtain_cars.json', 'w') as file:
                json.dump(car_positions, file)
        except json.JSONDecodeError as e:
            print(f"Error al escribir en el archivo JSON: {e}")


    def json_state_semaforo(self):
        print("Generando estados de semáforos para JSON.")  # Mensaje Debug
        semaforo_states = []
        for agent in self.schedule.agents:
            if isinstance(agent, Building) and agent.is_semaforo:
                semaforo_data = {
                    "id": agent.unique_id,
                    "position": [agent.pos[0], agent.pos[1]],
                    "state": agent.state
                }
                semaforo_states.append(semaforo_data)

        try:
            with open('obtain_state_semaforos.json', 'w') as file:
                json.dump(semaforo_states, file)
        except json.JSONDecodeError as e:
            print(f"Error al escribir en el archivo JSON: {e}")

class Car(Agent):
    def __init__(self, unique_id, model, start_position, end_position):
        super().__init__(unique_id, model)
        self.position = start_position
        self.end_position = end_position
        self.path = self.calculate_path(self.position, self.end_position)
        self.passengers = []  # Para llevar un registro de las personas en el coche
        self.color = "normal_color"
        self.last_position = None


    def on_grid(self, pos):
        """ Verifica si la posición está dentro de los límites del grid. """
        x, y = pos
        return 0 <= x < self.model.grid.width and 0 <= y < self.model.grid.height

    # TODO 1: Obtener posicion de los coches
    def obtain_position(self):
        x, y = self.position
        unity_elevation = 2

        return [x, unity_elevation, y]

    def obtain_direction(self):
        if not self.last_position:
            return None  # No se puede determinar la dirección sin una posición anterior

        x_diff = self.position[0] - self.last_position[0]
        y_diff = self.position[1] - self.last_position[1]

        if x_diff == 0 and y_diff > 0:
            return 'N'
        elif x_diff == 0 and y_diff < 0:
            return 'S'
        elif x_diff > 0 and y_diff == 0:
            return 'E'
        elif x_diff < 0 and y_diff == 0:
            return 'W'
        elif x_diff > 0 and y_diff > 0:
            return 'NE'
        elif x_diff < 0 and y_diff > 0:
            return 'NW'
        elif x_diff > 0 and y_diff < 0:
            return 'SE'
        elif x_diff < 0 and y_diff < 0:
            return 'SW'
        else:
            return None  # En caso de que el coche no se haya movido

    # Metodo para modificar la posición acorde a lo que Unity nos da
    def modify_position_based_on_direction(self, position, direction):
        modified_position = list(position)

        if direction in ['N', 'S']:
            modified_position[1] += 0.6 if direction == 'N' else -0.6
        elif direction in ['E', 'W']:
            modified_position[0] += 0.6 if direction == 'E' else -0.6
        elif direction == 'NW':
            modified_position[0] -= 0.6
            modified_position[1] += 0.6
        elif direction == 'NE':
            modified_position[0] += 0.6
            modified_position[1] += 0.6
        elif direction == 'SW':
            modified_position[0] -= 0.6
            modified_position[1] -= 0.6
        elif direction == 'SE':
            modified_position[0] += 0.6
            modified_position[1] -= 0.6

        print(modified_position)

        return tuple(modified_position) 
    
    def get_possible_steps(self, direction_sign):
        """ Devuelve los posibles pasos basados en la señal de dirección. """
        if direction_sign == 'N':
            return [(0, 1)]
        elif direction_sign == 'S':
            return [(0, -1)]
        elif direction_sign == 'E':
            return [(1, 0)]
        elif direction_sign == 'W':
            return [(-1, 0)]
        elif direction_sign == 'NW':
            return [(0, 1), (-1, 0)]
        elif direction_sign == 'NE':
            return [(0, 1), (1, 0)]
        elif direction_sign == 'SW':
            return [(0, -1), (-1, 0)]
        elif direction_sign == 'SE':
            return [(0, -1), (1, 0)]
        else:
            # Si no hay dirección específica, se consideran todas las direcciones
            return [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 1), (-1, 0), (0, 1), (1, 0), (0, -1), (-1, 0), (0, -1), (1, 0)]
        
    def is_directly_in_front(self, pos, next_post):
        """ Verifica si la posición está directamente al frente del coche. """
        # Asumiendo que `next_pos` es la siguiente posición en la ruta del coche
        return pos == next_post

    def is_occupied(self, pos):
        """ Verifica si una celda está ocupada por un estacionamiento, un edificio, un coche o un semáforo en rojo. """
        if pos in self.model.parking_spots:
            return False  # La celda es un estacionamiento y está accesible

        for edificio in self.model.edificios:
            x, y, width, height = edificio
            if x <= pos[0] < x + width and y <= pos[1] < y + height:
                return True  # Ocupada por un edificio

        # Verificar si hay un semáforo en rojo en la posición
        cell_contents = self.model.grid.get_cell_list_contents(pos)
        for obj in cell_contents:
            if isinstance(obj, Building) and obj.is_semaforo and obj.state == 'red':
                return True  # Ocupada por un semáforo en rojo

        return False

    def distance(self, pos1, pos2):
        """ Calcula la distancia de Manhattan entre dos posiciones. """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_neighbors(self, pos):
        """ Devuelve los vecinos accesibles de una posición dada, respetando las señales de tráfico. """
        direction_sign = self.check_for_direction_sign_at(pos)
        possible_steps = self.get_possible_steps(direction_sign)

        neighbors = []
        for step in possible_steps:
            new_position = (pos[0] + step[0], pos[1] + step[1])
            if self.on_grid(new_position) and not self.is_occupied(new_position):
                neighbors.append(new_position)
        return neighbors

    def check_for_direction_sign_at(self, pos):
        """ Busca una señal de tráfico en una posición dada y devuelve su dirección. """
        cell_contents = self.model.grid.get_cell_list_contents(pos)
        for obj in cell_contents:
            if isinstance(obj, RoadSign):
                return obj.direction
        return None

    def calculate_path(self, start, goal):
        """ Calcula el camino más corto utilizando el algoritmo A*. """
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.distance(start, goal)}

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for neighbor in self.get_neighbors(current):
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.distance(neighbor, goal)
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []
    
    def remove_from_model(self):
        if self.unique_id in self.model.schedule._agents:  # Verifica si el agente está en el schedule
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
    
    def step(self):
        # Se guarda la informacion del ultimo movimiento para ser almacenada como el movimiento actual
        self.last_position = self.position[:]

        # Recalcular camino si es necesario
        if not self.path or not self.path_valid():
            self.path = self.calculate_path(self.position, self.end_position)

        # Continuar con la lógica de movimiento
        if self.path:
            next_position = self.path[0]

            # Verificar si la siguiente posición está ocupada por otro coche
            if self.is_position_occupied_by_car(next_position):
                # Intentar encontrar un paso alternativo
                for step in self.get_possible_steps(None):  # Considerar todas las direcciones
                    alternative_next_position = (self.position[0] + step[0], self.position[1] + step[1])
                    if self.on_grid(alternative_next_position) and not self.is_occupied(alternative_next_position):
                        cell_contents = self.model.grid.get_cell_list_contents(alternative_next_position)
                        if not any(isinstance(obj, Building) and obj.is_semaforo and obj.state == 'red' for obj in cell_contents):
                            self.model.grid.move_agent(self, alternative_next_position)
                            self.position = alternative_next_position
                            self.path = self.calculate_path(self.position, self.end_position)
                            return

            # Verificar si hay un semáforo en rojo en la siguiente posición
            elif self.is_semaphore_red(next_position):
                return  # Detenerse si hay un semáforo en rojo

            # Moverse a la siguiente posición si está libre
            if not self.is_occupied(next_position):
                self.model.grid.move_agent(self, next_position)
                self.position = next_position
                self.path.pop(0)

                # Verificar si el vehículo ha llegado a su destino
                if self.position == self.end_position:
                    self.remove_from_model()  # Eliminar el coche del modelo
                    return

        print("Current step: ", self.position)


    def remove_from_model(self):
        # Lógica para eliminar el coche del modelo
        self.model.schedule.remove(self)

    def is_position_occupied_by_car(self, pos):
        """ Verifica si la posición está ocupada por otro coche. """
        cell_contents = self.model.grid.get_cell_list_contents(pos)
        return any(isinstance(obj, Car) for obj in cell_contents)

    def is_semaphore_red(self, pos):
        cell_contents = self.model.grid.get_cell_list_contents(pos)
        for obj in cell_contents:
            if isinstance(obj, Building) and obj.is_semaforo and obj.state == 'red':
                return True
        return False
    
    def path_valid(self):
        """ Verifica si el camino actual sigue siendo válido. """
        for pos in self.path:
            if self.is_position_occupied_by_car(pos) or self.is_semaphore_red(pos) or self.is_occupied(pos):
                return False
        return True
    
    def choose_new_destination(self):
        """ Elige un nuevo destino para el coche. """
        if not self.model.parking_spots:
            return self.position  # No cambiar de destino si no hay estacionamientos

        # Elegir un destino aleatorio que no sea la posición actual
        new_destinations = [spot for spot in self.model.parking_spots if spot != self.position]
        return random.choice(new_destinations) if new_destinations else self.position 



