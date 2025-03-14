import pygame
import threading
import queue
import comands  # импортируем все функции и глобальные переменные из comands.py

def input_thread(input_queue):
    """Поток, который постоянно ждёт ввода из консоли."""
    while True:
        user_input = input()
        input_queue.put(user_input)

def main():
    pygame.init()

    # --- 1) Определяем разрешение экрана ---
    info = pygame.display.Info()
    screen_w, screen_h = info.current_w, info.current_h
    print("Разрешение экрана:", screen_w, "x", screen_h)

    # --- 2) Загружаем карту ---
    try:
        raw_map_image = pygame.image.load("assets/map.png")
    except Exception as e:
        print("Ошибка загрузки карты:", e)
        return

    map_width, map_height = raw_map_image.get_width(), raw_map_image.get_height()
    print("Исходный размер карты:", map_width, "x", map_height)

    # --- 3) Вычисляем масштаб ---
    scale = min(
        (screen_w * 0.9) / map_width,
        (screen_h * 0.9) / map_height,
        1.0
    )
    scaled_map_width = int(map_width * scale)
    scaled_map_height = int(map_height * scale)
    print("Итоговый размер карты:", scaled_map_width, "x", scaled_map_height)
    print("Масштаб:", scale)

    # --- 4) Создаём окно ---
    screen = pygame.display.set_mode((scaled_map_width, scaled_map_height))
    pygame.display.set_caption("Airport Visualizer")

    # Масштабируем карту
    map_image = pygame.transform.smoothscale(raw_map_image, (scaled_map_width, scaled_map_height)).convert()

    clock = pygame.time.Clock()

    # --- 5) Запуск потока ввода команд ---
    input_queue = queue.Queue()
    thread = threading.Thread(target=input_thread, args=(input_queue,), daemon=True)
    thread.start()

    # --- 6) Масштабируем изображение самолёта (команда /plane) ---
    plane_factor = 0.2
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

    # --- 7) Масштабируем изображения машин (команда /car) ---
    # Машина должна быть в 2 раза меньше самолёта (при plane_factor=0.2 => car_factor=0.1)
    car_factor = 0.1
    for model, orig_image in comands.car_images_original.items():
        if comands.car_images_scaled.get(model) is None:
            w_orig, h_orig = orig_image.get_size()
            new_w = int(w_orig * scale * car_factor)
            new_h = int(h_orig * scale * car_factor)
            new_w = max(new_w, 1)
            new_h = max(new_h, 1)
            comands.car_images_scaled[model] = pygame.transform.smoothscale(orig_image, (new_w, new_h))
            print(f"Машина {model} после масштабирования: {new_w}x{new_h}")

    # --- 8) Коэффициент для GIF-анимаций /action ---
    action_factor = 0.25

    running = True
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Обработка команд из консоли
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
                            comands.plane_image_scaled = pygame.transform.smoothscale(comands.plane_image_original, (new_w, new_h))
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
                elif parts[0] == "/action":
                    # Новая команда /action <Name> <Point>
                    comands.command_action(parts[1:])
                else:
                    print("Неизвестная команда")
            else:
                print("не команда")

        # Отрисовка карты
        screen.blit(map_image, (0, 0))

        # Отрисовка самолётов (/plane)
        for plane_id, plane_data in list(comands.planes.items()):
            route = plane_data.get("route", [])
            idx = plane_data.get("route_index", 1)
            if idx < len(route):
                current_vertex = route[idx - 1]
                target_vertex = route[idx]
                current_pos = comands.point_coords.get(current_vertex, (plane_data["x"], plane_data["y"]))
                target_pos = comands.point_coords.get(target_vertex, current_pos)
                dx = target_pos[0] - plane_data["x"]
                dy = target_pos[1] - plane_data["y"]
                dist = (dx**2 + dy**2) ** 0.5

                if dist < plane_data["speed"]:
                    plane_data["x"], plane_data["y"] = target_pos
                    plane_data["route_index"] += 1
                    plane_data["current_node"] = target_vertex
                else:
                    plane_data["x"] += plane_data["speed"] * dx / dist
                    plane_data["y"] += plane_data["speed"] * dy / dist
            else:
                if plane_data.get("removing", False):
                    del comands.planes[plane_id]
                    continue
            if plane_id in comands.planes:
                draw_x = plane_data["x"] * scale
                draw_y = plane_data["y"] * scale
                if comands.plane_image_scaled:
                    plane_rect = comands.plane_image_scaled.get_rect()
                    plane_rect.center = (draw_x, draw_y)
                    screen.blit(comands.plane_image_scaled, plane_rect)

        # Отрисовка машин (/car)
        for model, car_data in list(comands.cars.items()):
            route = car_data.get("route", [])
            idx = car_data.get("route_index", 1)
            if idx < len(route):
                current_vertex = route[idx - 1]
                target_vertex = route[idx]
                current_pos = comands.point_coords.get(current_vertex, (car_data["x"], car_data["y"]))
                target_pos = comands.point_coords.get(target_vertex, current_pos)
                dx = target_pos[0] - car_data["x"]
                dy = target_pos[1] - car_data["y"]
                dist = (dx**2 + dy**2) ** 0.5

                if dist < car_data["speed"]:
                    car_data["x"], car_data["y"] = target_pos
                    car_data["route_index"] += 1
                else:
                    car_data["x"] += car_data["speed"] * dx / dist
                    car_data["y"] += car_data["speed"] * dy / dist
            else:
                if route and route[-1] == car_data.get("start_origin"):
                    del comands.cars[model]
                    continue
            if model in comands.cars:
                draw_x = car_data["x"] * scale
                draw_y = car_data["y"] * scale
                if model in comands.car_images_scaled and comands.car_images_scaled[model]:
                    car_image = comands.car_images_scaled[model]
                    car_rect = car_image.get_rect()
                    car_rect.center = (draw_x, draw_y)
                    screen.blit(car_image, car_rect)

        # Отрисовка анимаций /action
        # Здесь используем кадры, которые были загружены с помощью Pillow
        now = pygame.time.get_ticks()
        for action_id, action_data in list(comands.actions.items()):
            start_time = action_data["start_time"]
            duration = action_data["duration"]
            if now - start_time > duration:
                del comands.actions[action_id]
                continue

            name = action_data["name"]
            # Если для данного имени ещё не выполнено масштабирование, масштабируем все кадры
            if name not in comands.action_frames_scaled or comands.action_frames_scaled[name] is None:
                scaled_frames = []
                for frame in comands.action_frames[name]:
                    w_orig, h_orig = frame.get_size()
                    new_w = int(w_orig * scale * action_factor)
                    new_h = int(h_orig * scale * action_factor)
                    new_w = max(new_w, 1)
                    new_h = max(new_h, 1)
                    scaled_frame = pygame.transform.smoothscale(frame, (new_w, new_h))
                    scaled_frames.append(scaled_frame)
                comands.action_frames_scaled[name] = scaled_frames

            elapsed = now - start_time
            frames_list = comands.action_frames[name]
            n_frames = len(frames_list)
            # Рассчитываем индекс кадра: линейное распределение по длительности анимации
            frame_index = int((elapsed / duration) * n_frames)
            if frame_index >= n_frames:
                frame_index = n_frames - 1
            current_frame = comands.action_frames_scaled[name][frame_index]
            draw_x = action_data["x"] * scale
            draw_y = action_data["y"] * scale
            rect = current_frame.get_rect()
            rect.center = (draw_x, draw_y)
            screen.blit(current_frame, rect)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()

if __name__ == '__main__':
    main()
