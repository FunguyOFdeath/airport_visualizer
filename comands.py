# comands.py

import pygame
from collections import deque
from ways import ways
from points import points

# Построение неориентированного графа на основе списка путей
graph = {}
for way in ways:
    a = way['p1']
    b = way['p2']
    graph.setdefault(a, []).append(b)
    graph.setdefault(b, []).append(a)

# Словарь координат точек
point_coords = {pt['point']: (pt['x'], pt['y']) for pt in points}

# Глобальные переменные для самолётов
planes = {}                   # {номер: данные самолёта}
plane_image_original = None   # Оригинальная картинка (plane.png) без масштабирования
plane_image_scaled = None     # Масштабированная картинка (задаётся в main.py, один раз)

def bfs_path(start, end, graph):
    """
    Поиск маршрута от start до end с помощью BFS.
    Возвращает список вершин или пустой список, если маршрут не найден.
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
    /way <start> <end>
    Возвращает маршрут (список вершин) или пустой список.
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
    Если самолёта нет, создаём, маршрут от RW-0 до свободного гейта.
    Если самолёт есть, строим маршрут от его текущей вершины до RW-0 (улетает).
    """
    global planes, plane_image_original, plane_image_scaled
    if len(parts) != 1:
        print("Неверный формат команды. Используйте: /plane <номер>")
        return None

    try:
        plane_id = int(parts[0])
    except ValueError:
        print("Ошибка: некорректный номер самолёта.")
        return None

    # Если самолёт уже существует – направляем его на RW-0
    if plane_id in planes:
        plane = planes[plane_id]
        current_node = plane.get('current_node', "RW-0")
        route_to_rw = command_way([current_node, "RW-0"])
        if route_to_rw and route_to_rw[-1] == "RW-0":
            plane['route'] = route_to_rw
            plane['route_index'] = 1
            plane['removing'] = True  # пометка для удаления
        return plane.get('route', [])

    # Если самолёта нет, создаём нового (максимум 5 одновременно)
    if len(planes) >= 5:
        print("Ошибка: превышен лимит самолётов (максимум 5).")
        return None

    # Выбираем свободный гейт
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

    # Маршрут от RW-0 до выбранного гейта
    route_to_gate = command_way(["RW-0", chosen_gate])
    if not route_to_gate or route_to_gate[-1] != chosen_gate:
        print(f"Ошибка: маршрут до {chosen_gate} не найден.")
        return None

    # Начальные координаты самолёта – RW-0
    x0, y0 = point_coords.get("RW-0", (0, 0))

    # Если оригинал самолёта ещё не загружен, загружаем
    if plane_image_original is None:
        try:
            plane_image_original = pygame.image.load("assets/plane.png").convert_alpha()
        except Exception as e:
            print("Ошибка загрузки plane.png:", e)
            return None
        # plane_image_scaled остаётся None — мы её будем задавать один раз в main.py

    # Создаём запись о новом самолёте
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
