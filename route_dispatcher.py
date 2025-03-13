import heapq
import time


class AirportDispatcher:
    def __init__(self):
        """ Инициализация диспетчера, загрузка всех точек и соединений """
        self.graph = {}  # Карта аэропорта: {узел: [(сосед, тип пути), ...]}
        self.occupied_nodes = {}  # Занятые узлы
        self.occupied_edges = {}  # Занятые дороги
        self.queues = {}  # Очереди техники в узлах
        self.initialize_map()

    def initialize_map(self):
        """ Полная схема аэропорта с узлами и дорогами """
        self.graph = {
            # Взлетная полоса и рулежные дорожки
            "RW-1": [("E-37", "runway")],
            "E-37": [("RW-1", "runway"), ("RE-1", "taxiway")],
            "RE-1": [("E-37", "taxiway"), ("E-38", "taxiway")],
            "E-38": [("RE-1", "taxiway"), ("PCR-5", "taxiway")],

            # Парковочные зоны для самолетов
            "PCR-5": [("E-38", "taxiway"), ("P-5", "parking")],
            "P-5": [("PCR-5", "parking"), ("CP-51", "service"), ("CP-52", "service")],
            "PCR-4": [("E-38", "taxiway"), ("P-4", "parking")],
            "P-4": [("PCR-4", "parking"), ("CP-41", "service"), ("CP-42", "service")],
            "PCR-3": [("E-38", "taxiway"), ("P-3", "parking")],
            "P-3": [("PCR-3", "parking"), ("CP-31", "service"), ("CP-32", "service")],
            "PCR-2": [("E-38", "taxiway"), ("P-2", "parking")],
            "P-2": [("PCR-2", "parking"), ("CP-21", "service"), ("CP-22", "service")],
            "PCR-1": [("E-38", "taxiway"), ("P-1", "parking")],
            "P-1": [("PCR-1", "parking"), ("CP-11", "service"), ("CP-12", "service")],

            # Основные дороги для машин
            "CR-1": [("E-11", "road"), ("E-30", "road"), ("E-31", "road")],
            "E-11": [("CR-1", "road"), ("CR-2", "road")],
            "CR-2": [("E-11", "road"), ("E-12", "road")],
            "E-12": [("CR-2", "road"), ("CR-3", "road")],
            "CR-3": [("E-12", "road"), ("E-13", "road")],
            "E-13": [("CR-3", "road"), ("CR-4", "road")],
            "CR-4": [("E-13", "road"), ("E-14", "road")],
            "E-14": [("CR-4", "road"), ("CR-5", "road")],
            "CR-5": [("E-14", "road"), ("E-33", "road")],

            # Ворота и терминалы
            "G-11": [("E-15", "gate")],
            "E-15": [("CR-1", "road"), ("G-11", "gate")],
            "G-12": [("E-16", "gate")],
            "E-16": [("CR-1", "road"), ("G-12", "gate")],
            "G-21": [("E-19", "gate")],
            "E-19": [("CR-2", "road"), ("G-21", "gate")],
            "G-22": [("E-20", "gate")],
            "E-20": [("CR-2", "road"), ("G-22", "gate")],

            # Склады и ангары
            "CG-1": [("E-33", "garage")],
            "E-33": [("CR-5", "road"), ("CG-1", "garage")],
            "BW-1": [("E-32", "warehouse")],
            "E-32": [("CR-1", "road"), ("BW-1", "warehouse")],

            # Заправка и выход
            "FS-1": [("E-35", "fuel")],
            "E-35": [("FS-1", "fuel"), ("E-36", "road")],
            "RS-1": [("E-34", "road")],
            "E-34": [("RS-1", "road"), ("E-35", "road")],
        }

        # Инициализация занятости узлов
        for node in self.graph:
            self.occupied_nodes[node] = None
            self.queues[node] = []

    def get_shortest_path(self, start, goal):
        """ Вычисляет кратчайший путь от start до goal. """
        queue = []
        heapq.heappush(queue, (0, start, []))
        visited = set()

        while queue:
            cost, node, path = heapq.heappop(queue)
            if node in visited:
                continue
            path = path + [node]
            if node == goal:
                return path

            visited.add(node)
            for neighbor, _ in self.graph.get(node, []):
                if neighbor not in visited:
                    heapq.heappush(queue, (cost + 1, neighbor, path))

        return None  # Путь не найден

    def request_move(self, vehicle_id, vehicle_type, current, destination):
        """ Запрашивает разрешение на движение. """
        if self.occupied_nodes.get(destination) is None:
            self.occupied_nodes[current] = None
            self.occupied_nodes[destination] = vehicle_id
            return True
        else:
            self.queues[destination].append(vehicle_id)
            return False

    def release_node(self, vehicle_id, node):
        """ Освобождает узел и проверяет очередь. """
        if self.occupied_nodes.get(node) == vehicle_id:
            self.occupied_nodes[node] = None
            if self.queues[node]:
                next_vehicle = self.queues[node].pop(0)
                self.occupied_nodes[node] = next_vehicle

    def move_vehicle(self, vehicle_id, vehicle_type, start, goal):
        """ Двигает технику шаг за шагом, избегая столкновений. """
        path = self.get_shortest_path(start, goal)
        if not path:
            print(f"Ошибка: путь от {start} до {goal} не найден.")
            return

        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]

            while not self.request_move(vehicle_id, vehicle_type, current, next_node):
                time.sleep(1)  # Ждём, пока узел освободится

            print(f"{vehicle_type} {vehicle_id} движется из {current} в {next_node}")
            time.sleep(1)  # Симуляция передвижения

            self.release_node(vehicle_id, current)

        print(f"{vehicle_type} {vehicle_id} достиг {goal}")


# Тест диспетчера
if __name__ == "__main__":
    dispatcher = AirportDispatcher()
    dispatcher.move_vehicle("Plane_1", "plane", "RW-1", "P-5")
    dispatcher.move_vehicle("Car_1", "car", "G-11", "BW-1")
