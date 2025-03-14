import pygame
from collections import deque
from ways import ways
from points import points
import math

# ------------------ ПОСТРОЕНИЕ ГРАФА ------------------ #
graph = {}
for way in ways:
    a = way.get('p1') or way.get('point1')
    b = way.get('p2') or way.get('point2')
    if a and b:
        graph.setdefault(a, []).append(b)
        graph.setdefault(b, []).append(a)

point_coords = {pt['point']: (pt['x'], pt['y']) for pt in points}

# ------------------ САМОЛЁТЫ ( /plane ) ------------------ #
planes = {}                   # {номер_самолёта: данные}
plane_image_original = None
plane_image_scaled = None

# ------------------ МАШИНЫ ( /car ) ------------------ #
cars = {}  # {car_id: {...}}
next_car_id = 1  # Будем увеличивать при создании новой машины

car_images_original = {}  # {model: Surface}
car_images_scaled = {}    # {model: Surface}

ALLOWED_CAR_MODELS = {
    "baggage_tractor",
    "bus",
    "catering_truck",
    "followme",
    "fuel_truck",
    "passenger_gangway"
}

# ------------------ BFS ------------------ #
def bfs_path(start, end, graph):
    queue = deque([start])
    visited = {start}
    prev = {start: None}

    while queue:
        current = queue.popleft()
        if current == end:
            break
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                prev[neighbor] = current
                queue.append(neighbor)

    if end not in prev:
        return []
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path

def command_way(parts):
    """
    /way <start> <end>
    Возвращает маршрут (список вершин) или пустой список.
    """
    if len(parts) != 2:
        print("Неверный формат команды. /way <начало> <конец>")
        return []
    start, goal = parts[0], parts[1]
    if start not in graph:
        print(f"Точка {start} не найдена.")
        return []
    if goal not in graph:
        print(f"Точка {goal} не найдена.")
        return []
    route = bfs_path(start, goal, graph)
    if not route:
        print("Путь не найден.")
    return route

# ------------------ ЛОГИКА САМОЛЁТОВ ------------------ #
def command_plane(parts):
    """
    /plane <номер>
    (ЛОГИКА НЕ МЕНЯЕМ)
    """
    if len(parts) != 1:
        print("Неверный формат команды. /plane <номер>")
        return None

    try:
        plane_id = int(parts[0])
    except ValueError:
        print("Ошибка: некорректный номер самолёта.")
        return None

    if plane_id in planes:
        # Уже существует => отправляем на RW-0
        plane = planes[plane_id]
        current_node = plane.get('current_node', "RW-0")
        route_to_rw = command_way([current_node, "RW-0"])
        if route_to_rw and route_to_rw[-1] == "RW-0":
            plane['route'] = route_to_rw
            plane['route_index'] = 1
            plane['removing'] = True
        return plane.get('route', [])

    if len(planes) >= 5:
        print("Ошибка: превышен лимит самолётов (максимум 5).")
        return None

    gates_priority = ["P-5", "P-4", "P-3", "P-2", "P-1"]
    occupied_gates = {plane.get('gate') for plane in planes.values() if plane.get('gate')}
    chosen_gate = None
    for gate in gates_priority:
        if gate not in occupied_gates:
            chosen_gate = gate
            break
    if chosen_gate is None:
        print("Ошибка: нет свободных гейтов.")
        return None

    route_to_gate = command_way(["RW-0", chosen_gate])
    if not route_to_gate or route_to_gate[-1] != chosen_gate:
        print(f"Ошибка: маршрут до {chosen_gate} не найден.")
        return None

    x0, y0 = point_coords.get("RW-0", (0, 0))

    global plane_image_original
    if plane_image_original is None:
        try:
            plane_image_original = pygame.image.load("assets/plane.png").convert_alpha()
        except Exception as e:
            print("Ошибка загрузки plane.png:", e)
            return None

    planes[plane_id] = {
        "id": plane_id,
        "x": x0, "y": y0,
        "route": route_to_gate,
        "route_index": 1,
        "gate": chosen_gate,
        "removing": False,
        "speed": 10.0,
        "current_node": "RW-0",
    }
    return planes[plane_id]['route']

# ------------------ ЛОГИКА МАШИН ------------------ #

def is_car_at_node(car_data, node, threshold=2.0):
    """Проверяем, находится ли машина car_data физически в точке node (по координатам)."""
    if node not in point_coords:
        return False
    nx, ny = point_coords[node]
    dx = nx - car_data["x"]
    dy = ny - car_data["y"]
    dist = math.hypot(dx, dy)
    return dist < threshold  # если ближе threshold пикселей, считаем, что "стоит" в узле

def command_car(parts):
    """
    /car <model> <origin> <destination>
    - Если уже есть машина с таким model, которая физически находится в <origin>,
      то перестраиваем маршрут от <origin> до <destination>.
    - Иначе создаём новую машину.
    - Машина удаляется, когда вернётся в свою точку car["origin"].
    """
    global next_car_id

    if len(parts) != 3:
        print("Неверный формат команды. /car <model> <origin> <destination>")
        return None

    model, origin, destination = parts
    if model not in ALLOWED_CAR_MODELS:
        print(f"Ошибка: модель {model} не поддерживается.")
        return None
    if origin not in point_coords:
        print(f"Ошибка: точка {origin} не найдена.")
        return None
    if destination not in point_coords:
        print(f"Ошибка: точка {destination} не найдена.")
        return None

    # Ищем существующую машину с таким model, которая стоит в origin
    for cid, car_data in cars.items():
        if car_data["model"] == model:
            # Проверяем, действительно ли она в узле origin
            if is_car_at_node(car_data, origin):
                # Перестраиваем маршрут
                new_route = command_way([origin, destination])
                if not new_route:
                    print("Путь не найден.")
                    return None
                car_data["route"] = new_route
                car_data["route_index"] = 1
                print(f"Машина {model} (ID={cid}) теперь едет из {origin} в {destination}: {new_route}")
                return new_route

    # Если не нашли подходящую машину – создаём новую
    route = command_way([origin, destination])
    if not route or route[-1] != destination:
        print("Путь не найден.")
        return None

    start_x, start_y = point_coords[origin]
    car_data = {
        "id": next_car_id,
        "model": model,
        "x": start_x,
        "y": start_y,
        "route": route,
        "route_index": 1,
        "origin": origin,  # Запоминаем исходную точку
        "speed": 5.0,
    }
    cars[next_car_id] = car_data
    next_car_id += 1

    # Загружаем картинку, если не загружена
    if model not in car_images_original:
        try:
            car_images_original[model] = pygame.image.load(f"assets/{model}.png").convert_alpha()
            car_images_scaled[model] = None
        except Exception as e:
            print(f"Ошибка загрузки {model}.png:", e)
            del cars[car_data["id"]]
            return None

    print(f"Создана машина {model} (ID={car_data['id']}) из {origin} в {destination}: {route}")
    return route
