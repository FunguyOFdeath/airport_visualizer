import pygame
import threading
import queue
import comands  # Импортируем функции и глобальные переменные из comands.py


def input_thread(input_queue):
    """Поток, который постоянно ждёт ввода из консоли."""
    while True:
        user_input = input()
        input_queue.put(user_input)


def main():
    pygame.init()

    # 1) Определяем разрешение экрана.
    info = pygame.display.Info()
    screen_w, screen_h = info.current_w, info.current_h
    print("Разрешение экрана:", screen_w, "x", screen_h)

    # 2) Загружаем карту.
    try:
        raw_map_image = pygame.image.load("assets/map.png")
    except Exception as e:
        print("Ошибка загрузки карты:", e)
        return

    map_width, map_height = raw_map_image.get_width(), raw_map_image.get_height()
    print("Исходный размер карты:", map_width, "x", map_height)

    # 3) Вычисляем масштаб, чтобы карта не выходила за 90% экрана.
    scale = min(
        (screen_w * 0.9) / map_width,
        (screen_h * 0.9) / map_height,
        1.0
    )
    scaled_map_width = int(map_width * scale)
    scaled_map_height = int(map_height * scale)
    print("Итоговый размер карты:", scaled_map_width, "x", scaled_map_height)
    print("Масштаб:", scale)

    # 4) Создаём окно.
    screen = pygame.display.set_mode((scaled_map_width, scaled_map_height))
    pygame.display.set_caption("Airport Visualizer")

    # Преобразуем карту к нужному размеру.
    map_image = pygame.transform.smoothscale(raw_map_image, (scaled_map_width, scaled_map_height)).convert()

    clock = pygame.time.Clock()

    # 5) Запуск потока ввода команд.
    input_queue = queue.Queue()
    thread = threading.Thread(target=input_thread, args=(input_queue,), daemon=True)
    thread.start()

    # 6) Масштабируем изображение самолёта (команда /plane).
    plane_factor = 0.2  # Коэффициент уменьшения для самолёта
    if comands.plane_image_original:
        w_orig, h_orig = comands.plane_image_original.get_size()
        new_w = int(w_orig * scale * plane_factor)
        new_h = int(h_orig * scale * plane_factor)
        new_w = max(new_w, 1)
        new_h = max(new_h, 1)
        comands.plane_image_scaled = pygame.transform.smoothscale(comands.plane_image_original, (new_w, new_h))
        print(f"Самолёт после масштабирования: {new_w}x{new_h}")
    else:
        print("Предупреждение: plane_image_original ещё не загружен в comands.py")

    # Масштабируем изображения для машин (команда /car).
    car_factor = 0.1  # Коэффициент масштабирования для машин
    for model, orig_image in comands.car_images_original.items():
        if comands.car_images_scaled.get(model) is None:
            w_orig, h_orig = orig_image.get_size()
            new_w = int(w_orig * scale * car_factor)
            new_h = int(h_orig * scale * car_factor)
            new_w = max(new_w, 1)
            new_h = max(new_h, 1)
            comands.car_images_scaled[model] = pygame.transform.smoothscale(orig_image, (new_w, new_h))
            print(f"Машина {model} после масштабирования: {new_w}x{new_h}")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Обработка команд из консоли.
        while not input_queue.empty():
            cmd_line = input_queue.get()
            if cmd_line.startswith("/"):
                parts = cmd_line.split()
                if parts[0] == "/way":
                    route = comands.command_way(parts[1:])
                    print("Маршрут:", route if route else "Не найден.")
                elif parts[0] == "/plane":
                    route = comands.command_plane(parts[1:])
                    if route:
                        print("Маршрут самолёта:", route)
                        if (comands.plane_image_original and comands.plane_image_scaled is None):
                            w_orig, h_orig = comands.plane_image_original.get_size()
                            new_w = int(w_orig * scale * plane_factor)
                            new_h = int(h_orig * scale * plane_factor)
                            new_w = max(new_w, 1)
                            new_h = max(new_h, 1)
                            comands.plane_image_scaled = pygame.transform.smoothscale(comands.plane_image_original,
                                                                                      (new_w, new_h))
                elif parts[0] == "/car":
                    route = comands.command_car(parts[1:])
                    if route:
                        print("Маршрут машины:", route)
                        model = parts[1]
                        if model in comands.car_images_original and comands.car_images_scaled.get(model) is None:
                            orig_image = comands.car_images_original[model]
                            w_orig, h_orig = orig_image.get_size()
                            new_w = int(w_orig * scale * car_factor)
                            new_h = int(h_orig * scale * car_factor)
                            new_w = max(new_w, 1)
                            new_h = max(new_h, 1)
                            comands.car_images_scaled[model] = pygame.transform.smoothscale(orig_image, (new_w, new_h))
                else:
                    print("Неизвестная команда")
            else:
                print("не команда")

        # 8) Рисуем карту.
        screen.blit(map_image, (0, 0))

        # 9) Двигаем и отрисовываем самолёты.
        for plane_id, plane_data in list(comands.planes.items()):
            route = plane_data.get("route", [])
            idx = plane_data.get("route_index", 1)
            if idx >= len(route):
                if plane_data.get("removing", False):
                    del comands.planes[plane_id]
                continue

            current_vertex = route[idx - 1]
            target_vertex = route[idx]

            current_pos = comands.point_coords.get(current_vertex, (plane_data["x"], plane_data["y"]))
            target_pos = comands.point_coords.get(target_vertex, current_pos)
            dx = target_pos[0] - plane_data["x"]
            dy = target_pos[1] - plane_data["y"]
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist < plane_data["speed"]:
                plane_data["x"], plane_data["y"] = target_pos
                plane_data["route_index"] += 1
                plane_data["current_node"] = target_vertex
            else:
                plane_data["x"] += plane_data["speed"] * dx / dist
                plane_data["y"] += plane_data["speed"] * dy / dist

            draw_x = plane_data["x"] * scale
            draw_y = plane_data["y"] * scale

            if comands.plane_image_scaled:
                plane_rect = comands.plane_image_scaled.get_rect()
                plane_rect.center = (draw_x, draw_y)
                screen.blit(comands.plane_image_scaled, plane_rect)

        # 10) Двигаем и отрисовываем машины.
        for origin, car_data in list(comands.cars.items()):
            route = car_data.get("route", [])
            idx = car_data.get("route_index", 1)
            if idx >= len(route):
                # Если машина достигла пункта назначения,
                # и если конечная точка совпадает с точкой создания, удаляем машину.
                if route[-1] == car_data["origin"]:
                    del comands.cars[origin]
                    continue
                else:
                    # Если машина приехала в другую точку, остаёмся на месте.
                    continue

            current_vertex = route[idx - 1]
            target_vertex = route[idx]

            current_pos = comands.point_coords.get(current_vertex, (car_data["x"], car_data["y"]))
            target_pos = comands.point_coords.get(target_vertex, current_pos)
            dx = target_pos[0] - car_data["x"]
            dy = target_pos[1] - car_data["y"]
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist < car_data["speed"]:
                car_data["x"], car_data["y"] = target_pos
                car_data["route_index"] += 1
            else:
                car_data["x"] += car_data["speed"] * dx / dist
                car_data["y"] += car_data["speed"] * dy / dist

            draw_x = car_data["x"] * scale
            draw_y = car_data["y"] * scale

            model = car_data["model"]
            if model in comands.car_images_scaled and comands.car_images_scaled[model]:
                car_image = comands.car_images_scaled[model]
                car_rect = car_image.get_rect()
                car_rect.center = (draw_x, draw_y)
                screen.blit(car_image, car_rect)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()


if __name__ == '__main__':
    main()
