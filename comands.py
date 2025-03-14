import pygame
from collections import deque
from ways import ways
from points import points

# Построение неориентированного графа на основе списка путей.
graph = {}
for way in ways:
    # Обрабатываем как формат из ways.py, так и из WAY.txt (ключи 'p1' и 'p2')
    a = way.get('p1') or way.get('point1')
    b = way.get('p2') or way.get('point2')
    if a and b:
        graph.setdefault(a, []).append(b)
        graph.setdefault(b, []).append(a)

# Словарь координат точек.
point_coords = {pt['point']: (pt['x'], pt['y']) for pt in points}

# Глобальные переменные для самолётов (команда /plane)
planes = {}                   # {номер: данные самолёта}
plane_image_original = None   # Оригинальное изображение самолёта (plane.png)
plane_image_scaled = None     # Масштабированное изображение самолёта (задаётся в main.py)

# Глобальные переменные для машин (команда /car)
cars = {}  # Ключ – точка создания (начало), считается уникальным идентификатором машины.
# Словари для хранения изображений машин по моделям.
car_images_original = {}  # {model: оригинальное изображение}
car_images_scaled = {}    # {model: масштабированное изображение}

# Допустимые модели машин.
ALLOWED_CAR_MODELS = {"baggage_tractor", "bus", "catering_truck", "followme", "fuel_truck", "passenger_gangway"}


def bfs_path(start, end, graph):
    """
    Поиск пути от start до end с использованием поиска в ширину (BFS).
    Возвращает список вершин или пустой список, если путь не найден.
    """
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
    /way <начало> <конец>
    Возвращает маршрут (список вершин) или пустой список, если маршрут не найден.
    """
    if len(parts) != 2:
        print("Неверный формат команды. Используйте: /way <начало> <конец>")
        return []
    start, goal = parts[0], parts[1]
    if start not in graph:
        print(f"Точка {start} не найдена в графе.")
        return []
    if goal not in graph:
        print(f"Точка {goal} не найдена в графе.")
        return []
    route = bfs_path(start, goal, graph)
    if not route:
        print("Путь не найден.")
    return route


def command_plane(parts):
    """
    /plane <номер>
    Если самолёт с указанным номером уже существует, строит для него маршрут из текущей точки до RW-0.
    Если самолёта нет – создаёт новый с маршрутом от RW-0 до свободного гейта.
    (Логика не изменяется – не трогаем /plane)
    """
    if len(parts) != 1:
        print("Неверный формат команды. Используйте: /plane <номер>")
        return None

    try:
        plane_id = int(parts[0])
    except ValueError:
        print("Ошибка: некорректный номер самолёта.")
        return None

    if plane_id in planes:
        plane = planes[plane_id]
        current_node = plane.get('current_node', "RW-0")
        route_to_rw = command_way([current_node, "RW-0"])
        if route_to_rw and route_to_rw[-1] == "RW-0":
            plane['route'] = route_to_rw
            plane['route_index'] = 1
            plane['removing'] = True  # пометка для удаления
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
        "canvas_item": None
    }
    return planes[plane_id]['route']


def command_car(parts):
    """
    /car <model> <начало> <конец>
    Если машины с данным идентификатором (точкой создания <начало>) нет, создаёт новую машину
    с указанной моделью, устанавливает её координаты в точке <начало> и вычисляет маршрут до <конец>.
    Если машина с данным идентификатором уже существует, обновляет для неё маршрут от текущей позиции до <конец>.
    Когда машина достигает точки, равной точке создания, она удаляется.
    """
    if len(parts) != 3:
        print("Неверный формат команды. Используйте: /car <model> <начало> <конец>")
        return None

    model, origin, destination = parts[0], parts[1], parts[2]

    if model not in ALLOWED_CAR_MODELS:
        print(f"Ошибка: модель {model} не поддерживается. Допустимые модели: {', '.join(ALLOWED_CAR_MODELS)}.")
        return None

    if origin not in point_coords:
        print(f"Ошибка: точка {origin} не найдена.")
        return None

    if destination not in point_coords:
        print(f"Ошибка: точка {destination} не найдена.")
        return None

    route = command_way([origin, destination])
    if not route or route[-1] != destination:
        print("Путь не найден.")
        return None

    # Если машина с данным идентификатором (точкой создания) уже существует, обновляем её маршрут.
    if origin in cars:
        car = cars[origin]
        car['route'] = route
        car['route_index'] = 1
        print(f"Обновлён маршрут для машины, созданной в {origin}: {route}")
        return route

    # Если машины нет, создаём новую.
    start_coords = point_coords[origin]
    car = {
        "model": model,
        "x": start_coords[0],
        "y": start_coords[1],
        "route": route,
        "route_index": 1,
        "origin": origin,  # Запоминаем точку создания
        "speed": 10.0,      # Скорость машины
    }
    cars[origin] = car

    # Загружаем изображение для данной модели, если оно ещё не загружено.
    if model not in car_images_original:
        try:
            car_images_original[model] = pygame.image.load(f"assets/{model}.png").convert_alpha()
            car_images_scaled[model] = None  # Будет масштабировано в main.py
        except Exception as e:
            print(f"Ошибка загрузки {model}.png:", e)
            del cars[origin]
            return None

    print(f"Создана машина {model} с маршрутом: {route}")
    return route
