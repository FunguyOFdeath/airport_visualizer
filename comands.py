import pygame
from collections import deque
from ways import ways
from points import points
from PIL import Image  # для работы с GIF

# -------------------- ГЛОБАЛЬНЫЕ ДАННЫЕ --------------------

# Построение неориентированного графа на основе списка путей.
graph = {}
for way in ways:
    a = way.get('p1') or way.get('point1')
    b = way.get('p2') or way.get('point2')
    if a and b:
        graph.setdefault(a, []).append(b)
        graph.setdefault(b, []).append(a)

# Словарь координат точек.
point_coords = {pt['point']: (pt['x'], pt['y']) for pt in points}

# -------------------- ДАННЫЕ ДЛЯ /plane --------------------
planes = {}  # {номер: данные самолёта}
plane_image_original = None  # Исходное изображение самолёта (plane.png)
plane_image_scaled = None  # Масштабированное изображение самолёта

# -------------------- ДАННЫЕ ДЛЯ /car --------------------
# Используем модель как ключ – только одна машина на модель.
cars = {}  # { model: { ... данные машины ... } }
car_images_original = {}  # { model: оригинальное изображение машины }
car_images_scaled = {}  # { model: масштабированное изображение машины }

ALLOWED_CAR_MODELS = {
    "baggage_tractor",
    "bus",
    "catering_truck",
    "followme",
    "fuel_truck",
    "passenger_gangway"
}

# -------------------- ДАННЫЕ ДЛЯ /action --------------------
# Словарь активных анимаций. Структура:
# actions[action_id] = {
#    "name": <имя GIF>,
#    "x": <логическая координата>,
#    "y": <логическая координата>,
#    "start_time": <pygame.time.get_ticks() в момент появления>,
#    "duration": 4000   # длительность в мс
# }
actions = {}

# Словарь, в котором для каждого допустимого имени хранится список кадров (Surface)
action_frames = {}
# Словарь для масштабированных кадров (аналог action_frames, но уже с учетом масштаба)
action_frames_scaled = {}

ALLOWED_ACTION_NAMES = {
    "baggage_man",
    "bus_passengers",
    "catering_man",
    "fuel_man"
}


# -------------------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ --------------------

def load_gif_frames(filename):
    """
    Загружает анимированный GIF из файла и разбивает его на кадры.
    Возвращает список pygame.Surface.
    """
    frames = []
    try:
        with Image.open(filename) as im:
            while True:
                frame = im.convert("RGBA")
                mode = frame.mode
                size = frame.size
                data = frame.tobytes()
                surface = pygame.image.fromstring(data, size, mode).convert_alpha()
                frames.append(surface)
                im.seek(im.tell() + 1)
    except EOFError:
        pass
    return frames


def bfs_path(start, end, graph):
    """
    Поиск кратчайшего пути от start до end с помощью поиска в ширину (BFS).
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


# -------------------- КОМАНДЫ --------------------

def command_way(parts):
    """
    /way <start> <end>
    Находит маршрут между точками start и end с помощью BFS.
    Возвращает список вершин или пустой список.
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
    Если самолёт с указанным номером уже существует – строит маршрут до RW-0.
    Если самолёта нет, создаёт нового (до 5 одновременно) с маршрутом от RW-0 до свободного гейта.
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
        "x": x0,
        "y": y0,
        "route": route_to_gate,
        "route_index": 1,
        "gate": chosen_gate,
        "removing": False,
        "speed": 10.0,
        "current_node": "RW-0",
    }
    return planes[plane_id]['route']


def get_car_current_node(car):
    """
    Определяет текущую вершину, на которой находится машина.
    Если машина движется между точками, возвращает последнюю достигнутую вершину.
    """
    route = car.get("route", [])
    idx = car.get("route_index", 1)
    if not route or idx < 1:
        return None
    if idx >= len(route):
        return route[-1]
    else:
        return route[idx - 1]


def command_car(parts):
    """
    /car <model> <origin> <destination>

    Если машины с данной моделью не существует, создаёт новую:
      - Начальные координаты берутся из вершины <origin>.
      - Вычисляется маршрут от <origin> до <destination> (BFS).
      - Запоминается начальная точка (start_origin) для удаления при возвращении.

    Если машина с данной моделью уже существует, обновляет её маршрут:
      - Берётся текущая позиция (через get_car_current_node).
      - Строится новый маршрут до <destination>.

    Машина удаляется, если маршрут завершается в точке start_origin.
    """
    if len(parts) != 3:
        print("Неверный формат команды. Используйте: /car <model> <origin> <destination>")
        return None

    model, origin, destination = parts
    if model not in ALLOWED_CAR_MODELS:
        print(f"Ошибка: модель {model} не поддерживается. Допустимые модели: {', '.join(ALLOWED_CAR_MODELS)}.")
        return None

    if origin not in point_coords:
        print(f"Ошибка: точка {origin} не найдена.")
        return None

    if destination not in point_coords:
        print(f"Ошибка: точка {destination} не найдена.")
        return None

    if model in cars:
        car = cars[model]
        current_node = get_car_current_node(car)
        if not current_node:
            current_node = origin
        new_route = bfs_path(current_node, destination, graph)
        if not new_route or new_route[-1] != destination:
            print("Путь не найден.")
            return None
        car["route"] = new_route
        car["route_index"] = 1
        print(f"Обновлён маршрут для {model}: {new_route}")
        return new_route

    route = bfs_path(origin, destination, graph)
    if not route or route[-1] != destination:
        print("Путь не найден.")
        return None

    start_x, start_y = point_coords[origin]
    cars[model] = {
        "model": model,
        "x": start_x,
        "y": start_y,
        "route": route,
        "route_index": 1,
        "speed": 5.0,
        "start_origin": origin,
    }

    if model not in car_images_original:
        try:
            car_images_original[model] = pygame.image.load(f"assets/{model}.png").convert_alpha()
            car_images_scaled[model] = None
        except Exception as e:
            print(f"Ошибка загрузки {model}.png:", e)
            del cars[model]
            return None

    print(f"Создана машина {model} из {origin} в {destination}: {route}")
    return route


def command_action(parts):
    """
    /action <Name> <Point>

    - Name: имя анимации (одно из ALLOWED_ACTION_NAMES)
    - Point: вершина карты (должна присутствовать в point_coords)

    После вызова анимация появляется на заданной точке, анимация проигрывается в течение 4 секунд и затем исчезает.
    При первом вызове для данного имени GIF разбивается на кадры с помощью Pillow.
    """
    if len(parts) != 2:
        print("Неверный формат команды. Используйте: /action <Name> <Point>")
        return

    name, point = parts
    if name not in ALLOWED_ACTION_NAMES:
        print(f"Ошибка: '{name}' не является допустимым именем. Допустимые: {ALLOWED_ACTION_NAMES}")
        return

    if point not in point_coords:
        print(f"Ошибка: точка {point} не найдена.")
        return

    x, y = point_coords[point]

    # Загружаем и разбиваем GIF на кадры, если ещё не загружено.
    if name not in action_frames:
        try:
            frames = load_gif_frames(f"animations/{name}.gif")
            if not frames:
                print(f"Не удалось загрузить кадры из GIF '{name}.gif'")
                return
            action_frames[name] = frames
            action_frames_scaled[name] = None  # Масштабирование выполнится в main.py
        except Exception as e:
            print(f"Ошибка загрузки GIF '{name}.gif': {e}")
            return

    # Создаём запись в actions с автоинкрементным ключом.
    action_id = len(actions) + 1
    actions[action_id] = {
        "name": name,
        "x": x,
        "y": y,
        "start_time": pygame.time.get_ticks(),
        "duration": 4000  # 4 секунды
    }

    print(f"Появляется анимация '{name}' на точке {point} (action_id={action_id})")
