import pygame
import sys
from vehicles.plane import Plane

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Airport Visualizer - Plane Movement")
    clock = pygame.time.Clock()

    # Загрузка карты и самолёта
    map_img = pygame.image.load("assets/map.png").convert()
    plane_img = pygame.image.load("assets/plane.png").convert_alpha()

    # Масштабирование самолёта, чтобы его размер не превышал размеры взлётной полосы (например, 100x100)
    max_width, max_height = 100, 100
    plane_rect = plane_img.get_rect()
    if plane_rect.width > max_width or plane_rect.height > max_height:
        plane_img = pygame.transform.scale(plane_img, (max_width, max_height))

    # Определение маршрутов (примерные координаты, подберите под вашу карту)
    # Маршрут приземления: от RW-1 (взлётно-посадочная полоса) через E-37, RE-1, E-38, PCR-5 до парковки P-5
    landing_route = [
        (200, 50),    # RW-1 (начало полосы)
        (300, 50),    # E-37
        (400, 100),   # RE-1
        (500, 150),   # E-38
        (600, 200),   # PCR-5
        (650, 250)    # P-5 (парковка)
    ]

    # Маршрут взлёта: обратный путь от парковки P-5 до RW-1
    takeoff_route = [
        (650, 250),   # P-5 (начало маршрута взлёта)
        (600, 200),   # PCR-5
        (500, 150),   # E-38
        (400, 100),   # RE-1
        (300, 50),    # E-37
        (200, 50)     # RW-1
    ]

    # В режиме FLYING самолёт летит по вектору (dx, dy) – например, вправо
    flying_vector = (1, 0)

    # Создаем объект Plane с маршрутом приземления и взлёта
    plane = Plane(image=plane_img, landing_route=landing_route, takeoff_route=takeoff_route, flying_vector=flying_vector, speed=2)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Отрисовка карты
        screen.blit(map_img, (0, 0))

        # Обновление состояния самолёта
        plane.update()

        # Если самолёт в режиме FLYING и улетел за пределы экрана, можно завершить его отрисовку
        # Здесь состояние plane.finished устанавливается в True
        if plane.finished:
            # В данном примере просто заливаем экран черным и выводим сообщение
            screen.fill((0, 0, 0))
            font = pygame.font.SysFont(None, 48)
            text = font.render("Plane has flown away", True, (255, 255, 255))
            screen.blit(text, (400, 360))
        else:
            # Отрисовка самолёта
            plane.draw(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main()
