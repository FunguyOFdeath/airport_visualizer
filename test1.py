import pygame

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Карта аэропорта v1 (повернута на 180°)")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BLUE = (0, 0, 255)
DARK_GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Координаты точек (повернуты на 180°: HEIGHT - y)
points = {
    "PCR-1": (100, HEIGHT - 700), "PCR-2": (200, HEIGHT - 700), "PCR-3": (300, HEIGHT - 700), "PCR-4": (400, HEIGHT - 700), "PCR-5": (500, HEIGHT - 700),
    "P-1": (100, HEIGHT - 650), "P-2": (200, HEIGHT - 650), "P-3": (300, HEIGHT - 650), "P-4": (400, HEIGHT - 650), "P-5": (500, HEIGHT - 650),
    "CP-11": (80, HEIGHT - 600), "CP-12": (120, HEIGHT - 600), "CP-21": (180, HEIGHT - 600), "CP-22": (220, HEIGHT - 600),
    "CP-31": (280, HEIGHT - 600), "CP-32": (320, HEIGHT - 600), "CP-41": (380, HEIGHT - 600), "CP-42": (420, HEIGHT - 600),
    "CP-51": (480, HEIGHT - 600), "CP-52": (520, HEIGHT - 600),
    "CR-1": (100, HEIGHT - 500), "CR-2": (200, HEIGHT - 500), "CR-3": (300, HEIGHT - 500), "CR-4": (400, HEIGHT - 500), "CR-5": (500, HEIGHT - 500),
    "G-11": (100, HEIGHT - 400), "G-12": (150, HEIGHT - 400), "G-21": (200, HEIGHT - 400), "G-22": (250, HEIGHT - 400), "G-31": (300, HEIGHT - 400),
    "G-32": (350, HEIGHT - 400), "G-41": (400, HEIGHT - 400), "G-42": (450, HEIGHT - 400), "G-51": (500, HEIGHT - 400), "G-52": (550, HEIGHT - 400),
    "BR-11": (100, HEIGHT - 300), "BR-21": (200, HEIGHT - 300), "BR-31": (300, HEIGHT - 300), "BR-41": (400, HEIGHT - 300), "BR-51": (500, HEIGHT - 300),
    "BW-1": (100, HEIGHT - 200), "EX-1": (150, HEIGHT - 200), "CG-1": (550, HEIGHT - 400), "RS-1": (550, HEIGHT - 300),
    "RW-1": (300, HEIGHT - 750), "RE-1": (500, HEIGHT - 700), "FS-1": (500, HEIGHT - 650)
}

# Пути (дороги между точками) с номерами
paths = [
    # Сектор PCR
    (("PCR-1", "PCR-2"), "E-42"), (("PCR-2", "PCR-3"), "E-41"), (("PCR-3", "PCR-4"), "E-40"),
    (("PCR-4", "PCR-5"), "E-39"), (("PCR-5", "RE-1"), "E-38"), (("RE-1", "RW-1"), "E-37"), (("RE-1", "FS-1"), "E-36"),
    # Соединения PCR → P
    (("PCR-1", "P-1"), "E-43"), (("PCR-2", "P-2"), "E-44"), (("PCR-3", "P-3"), "E-45"),
    (("PCR-4", "P-4"), "E-46"), (("PCR-5", "P-5"), "E-47"),
    # Соединения P → CP
    (("P-1", "CP-11"), "E-48"), (("P-1", "CP-12"), "E-49"), (("P-2", "CP-21"), "E-50"),
    (("P-2", "CP-22"), "E-51"), (("P-3", "CP-31"), "E-52"), (("P-3", "CP-32"), "E-53"),
    (("P-4", "CP-41"), "E-54"), (("P-4", "CP-42"), "E-55"), (("P-5", "CP-51"), "E-56"),
    (("P-5", "CP-52"), "E-57"),
    # Соединения CP → CR
    (("CP-11", "CR-1"), "E-1"), (("CP-12", "CR-1"), "E-4"), (("CP-21", "CR-2"), "E-2"), (("CP-22", "CR-2"), "E-5"),
    (("CP-31", "CR-3"), "E-3"), (("CP-32", "CR-3"), "E-6"), (("CP-41", "CR-4"), "E-7"), (("CP-42", "CR-4"), "E-8"),
    (("CP-51", "CR-5"), "E-9"), (("CP-52", "CR-5"), "E-10"),
    # Соединения CR
    (("CR-1", "CR-2"), "E-11"), (("CR-2", "CR-3"), "E-12"), (("CR-3", "CR-4"), "E-13"), (("CR-4", "CR-5"), "E-14"),
    # Соединения CR → X
    (("CR-1", "G-11"), "E-15"), (("CR-1", "G-12"), "E-16"), (("CR-1", "BR-11"), "E-17"),
    (("CR-2", "G-21"), "E-18"), (("CR-2", "G-22"), "E-19"), (("CR-2", "BR-21"), "E-20"),
    (("CR-3", "G-31"), "E-21"), (("CR-3", "G-32"), "E-22"), (("CR-3", "BR-31"), "E-23"),
    (("CR-4", "G-41"), "E-24"), (("CR-4", "G-42"), "E-25"), (("CR-4", "BR-41"), "E-26"),
    (("CR-5", "G-51"), "E-27"), (("CR-5", "G-52"), "E-28"), (("CR-5", "BR-51"), "E-29"),
    (("CR-5", "RS-1"), "E-33"), (("CR-5", "CG-1"), "E-34"),
    (("CR-1", "BW-1"), "E-30"), (("CR-1", "EX-1"), "E-31"), (("BW-1", "EX-1"), "E-32")
]
# Здания (повернуты на 180°)
buildings = {
    "BW-1": (80, HEIGHT - 160, 40, 40), "EX-1": (130, HEIGHT - 160, 40, 40), "CG-1": (530, HEIGHT - 360, 40, 40), "RS-1": (530, HEIGHT - 260, 40, 40),
    "G-11": (80, HEIGHT - 360, 40, 40), "G-12": (130, HEIGHT - 360, 40, 40), "G-21": (180, HEIGHT - 360, 40, 40), "G-22": (230, HEIGHT - 360, 40, 40),
    "G-31": (280, HEIGHT - 360, 40, 40), "G-32": (330, HEIGHT - 360, 40, 40), "G-41": (380, HEIGHT - 360, 40, 40), "G-42": (430, HEIGHT - 360, 40, 40),
    "G-51": (480, HEIGHT - 360, 40, 40), "G-52": (530, HEIGHT - 360, 40, 40),
    "BR-11": (80, HEIGHT - 260, 40, 40), "BR-21": (180, HEIGHT - 260, 40, 40), "BR-31": (280, HEIGHT - 260, 40, 40),
    "BR-41": (380, HEIGHT - 260, 40, 40), "BR-51": (480, HEIGHT - 260, 40, 40)
}

# Парковочные места (повернуты на 180°)
parking_spots = {
    "BW-1": [(80, HEIGHT - 340, 30, 20), (110, HEIGHT - 340, 30, 20), (140, HEIGHT - 340, 20, 20)],  # Bus, Bus, Luggage
    "RS-1": [(530, HEIGHT - 340, 30, 20), (560, HEIGHT - 340, 30, 20), (590, HEIGHT - 340, 20, 20)]   # Bus, Bus, Luggage
}

# Подписи для зданий
building_labels = {
    "BW-1": "Склад багажа", "EX-1": "Выход", "CG-1": "Гараж", "RS-1": "Лётный - место для пассажирских аэробусов",
    "G-11": "Г-11", "G-12": "Г-12", "G-21": "Г-21", "G-22": "Г-22", "G-31": "Г-31", "G-32": "Г-32",
    "G-41": "Г-41", "G-42": "Г-42", "G-51": "Г-51", "G-52": "Г-52",
    "BR-11": "БР-11", "BR-21": "БР-21", "BR-31": "БР-31", "BR-41": "БР-41", "BR-51": "БР-51"
}

# Функция для рисования пунктирной линии
def draw_dashed_line(surface, color, start_pos, end_pos, width=2, dash_length=10):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = x2 - x1
    dy = y2 - y1
    length = (dx**2 + dy**2)**0.5
    steps = int(length / dash_length)
    if steps == 0:
        return
    for i in range(steps + 1):
        if i % 2 == 0:  # Рисуем только чётные сегменты для пунктира
            start_x = x1 + dx * i / steps
            start_y = y1 + dy * i / steps
            end_x = x1 + dx * (i + 1) / steps if i < steps else x2
            end_y = y1 + dy * (i + 1) / steps if i < steps else y2
            pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), width)

# Главный цикл
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Очистка экрана
    screen.fill(WHITE)

    # Рисование дорог с разметкой и номерами
    font = pygame.font.Font(None, 12)
    for (start, end), label in paths:
        start_pos = points[start]
        end_pos = points[end]
        pygame.draw.line(screen, GRAY, start_pos, end_pos, 10)
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = (dx**2 + dy**2)**0.5
        steps = int(length / 20)
        for i in range(steps):
            if i % 2 == 0:
                x = start_pos[0] + dx * i / steps
                y = start_pos[1] + dy * i / steps
                pygame.draw.line(screen, WHITE, (x, y), (x + dx/steps, y + dy/steps), 2)
        if label:  # Отображаем номер только если он есть
            mid_x = (start_pos[0] + end_pos[0]) / 2
            mid_y = (start_pos[1] + end_pos[1]) / 2
            screen.blit(font.render(label, True, ORANGE), (mid_x - 15, mid_y - 10))

    # Рисование взлётно-посадочной полосы (сверху)
    pygame.draw.rect(screen, BLACK, (points["PCR-1"][0], points["RW-1"][1] - 10, 400, 20))
    pygame.draw.line(screen, YELLOW, (points["PCR-1"][0], points["RW-1"][1]), (points["PCR-5"][0], points["RW-1"][1]), 5)
    screen.blit(font.render("RW-1", True, ORANGE), (300, points["RW-1"][1] - 20))
    # Рисование точек
    for name, pos in points.items():
        if name.startswith("PCR"):
            pygame.draw.rect(screen, BLUE, (pos[0] - 15, pos[1] - 15, 30, 30))
            screen.blit(font.render(name, True, ORANGE), (pos[0] - 10, pos[1] - 35))
        elif name.startswith("P"):
            pygame.draw.rect(screen, BLUE, (pos[0] - 10, pos[1] - 10, 20, 20))
            screen.blit(font.render(name, True, ORANGE), (pos[0] - 10, pos[1] - 30))
        elif name.startswith("CP"):
            pygame.draw.polygon(screen, BLACK, [
                (pos[0], pos[1] - 10), (pos[0] + 10, pos[1]), (pos[0], pos[1] + 10), (pos[0] - 10, pos[1])
            ])
            screen.blit(font.render(name, True, ORANGE), (pos[0] - 10, pos[1] - 30))
        elif name.startswith("CR"):
            pygame.draw.circle(screen, DARK_GRAY, pos, 10)
            screen.blit(font.render(name, True, ORANGE), (pos[0] - 10, pos[1] - 30))
        elif name in ["BW-1", "EX-1", "CG-1", "RS-1", "G-11", "G-12", "G-21", "G-22", "G-31", "G-32",
                      "G-41", "G-42", "G-51", "G-52", "BR-11", "BR-21", "BR-31", "BR-41", "BR-51"]:
            pygame.draw.rect(screen, BLACK, (pos[0] - 15, pos[1] - 15, 30, 30))
            screen.blit(font.render(name, True, ORANGE), (pos[0] - 10, pos[1] - 35))
        elif name in ["RW-1", "RE-1", "FS-1"]:
            pygame.draw.circle(screen, BLACK, pos, 10)
            screen.blit(font.render(name, True, ORANGE), (pos[0] - 10, pos[1] - 30))

    # Рисование зданий с внутренними линиями
    for name, (x, y, w, h) in buildings.items():
        pygame.draw.rect(screen, BLACK, (x, y, w, h))
        pygame.draw.line(screen, WHITE, (x, y + h / 2), (x + w, y + h / 2), 2)

    # Рисование парковочных мест
    for name, spots in parking_spots.items():
        for i, (x, y, w, h) in enumerate(spots):
            pygame.draw.rect(screen, GRAY, (x, y, w, h))
            if i < 2:
                screen.blit(font.render("Bus", True, ORANGE), (x, y + 20))
            else:
                screen.blit(font.render("Luggage", True, ORANGE), (x, y + 20))

    # Подписи для зданий
    for name, label in building_labels.items():
        pos = points[name]
        screen.blit(font.render(label, True, BLACK), (pos[0] - len(label) * 3, pos[1] - 50))

    # Разделение на сектора (повернуто)
    pygame.draw.line(screen, BLACK, (0, HEIGHT - 600), (WIDTH, HEIGHT - 600), 5)  # Граница между CP и CR
    pygame.draw.line(screen, BLACK, (0, HEIGHT - 500), (WIDTH, HEIGHT - 500), 5)  # Граница между CR и X
    for x in range(0, WIDTH, 20):
        pygame.draw.line(screen, GRAY, (x, HEIGHT - 600), (x + 10, HEIGHT - 600), 2)
        pygame.draw.line(screen, GRAY, (x, HEIGHT - 500), (x + 10, HEIGHT - 500), 2)
    font = pygame.font.Font(None, 16)
    screen.blit(font.render("Сектор PCR (самолёты)", True, BLACK), (50, HEIGHT - 720))
    screen.blit(font.render("Сектор CR (машины)", True, BLACK), (50, HEIGHT - 520))
    screen.blit(font.render("Сектор X (терминал/ангар)", True, BLACK), (50, HEIGHT - 420))

    # Дополнительные подписи (повернуто)
    screen.blit(font.render("Место самолёта", True, BLACK), (150, HEIGHT - 760))
    screen.blit(font.render("Въезд на место самолёта - движение только в сторону, т.е движение ←", True, BLACK),
                (50, HEIGHT - 720))
    screen.blit(font.render("Гейт 1 - места для пассажирских автобусов", True, BLACK), (50, HEIGHT - 440))
    screen.blit(font.render("аэробус, одно направление багажа", True, BLACK), (550, HEIGHT - 440))

    # Символ самолёта над RW-1 (сверху)
    font_symbol = pygame.font.Font(None, 24)
    screen.blit(font_symbol.render("✈️", True, BLACK), (300, HEIGHT - 780))

    # Пунктирная линия для "Место самолёта"
    draw_dashed_line(screen, BLACK, (100, HEIGHT - 750), (500, HEIGHT - 750), width=2, dash_length=10)

    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

pygame.quit()