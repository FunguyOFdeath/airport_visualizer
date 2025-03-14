from collections import deque
from points import points
from ways import ways

# Построение неориентированного графа из списка путей
graph = {}
for way in ways:
    a = way['p1']
    b = way['p2']
    if a not in graph:
        graph[a] = []
    if b not in graph:
        graph[b] = []
    graph[a].append(b)
    graph[b].append(a)


def bfs_path(start, end, graph):
    """
    Поиск в ширину (BFS) для нахождения пути от start до end.
    Возвращает список точек, представляющих путь, или None, если путь не найден.
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
        return None

    # Восстанавливаем путь, идя от end к start
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path


def find_way_edge(p1, p2, ways):
    """
    Ищет в списке ways связь между двумя точками p1 и p2.
    Возвращает название пути (например, 'E-40') или None, если не найдено.
    """
    for way in ways:
        if (way['p1'] == p1 and way['p2'] == p2) or (way['p1'] == p2 and way['p2'] == p1):
            return way['way']
    return None


def process_command(command):
    """
    Обрабатывает команду вида /way point1 point2 и выводит найденный маршрут.
    """
    parts = command.strip().split()
    if len(parts) != 3 or parts[0] != '/way':
        print("Неверный формат команды. Используйте: /way point1 point2")
        return

    start = parts[1]
    end = parts[2]

    if start not in graph:
        print(f"Точка {start} не найдена в графе.")
        return
    if end not in graph:
        print(f"Точка {end} не найдена в графе.")
        return

    path = bfs_path(start, end, graph)
    if path is None:
        print("Путь не найден.")
        return

    print("Найденный маршрут:")
    print(" -> ".join(path))

    # Выводим названия путей между последовательными точками маршрута
    print("\nСоединяющие пути:")
    for i in range(len(path) - 1):
        edge_way = find_way_edge(path[i], path[i + 1], ways)
        print(f"{path[i]} -> {path[i + 1]} : {edge_way}")


if __name__ == '__main__':
    # Пример: пользователь вводит команду
    command = input("Введите команду (например, /way PCR-4 PCR-3): ")
    process_command(command)
