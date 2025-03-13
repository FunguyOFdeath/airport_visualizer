import pygame
import math
import time

class Plane:
    # Состояния самолёта
    STATE_LANDING = 0
    STATE_SERVICING = 1
    STATE_TAKEOFF = 2
    STATE_FLYING = 3

    def __init__(self, image, landing_route, takeoff_route, flying_vector, speed=2):
        """
        :param image:            Спрайт самолёта (pygame.Surface)
        :param landing_route:    Список координат (x, y) для маршрута приземления (до парковки)
        :param takeoff_route:    Список координат (x, y) для маршрута возвращения (от парковки до взлёта)
        :param flying_vector:    Направление движения в режиме FLYING (например, (dx, dy))
        :param speed:            Скорость движения в пикселях за обновление
        """
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect()

        # Начальные координаты – первая точка маршрута приземления
        self.x, self.y = landing_route[0]
        self.rect.center = (self.x, self.y)

        self.landing_route = landing_route
        self.takeoff_route = takeoff_route
        self.flying_vector = flying_vector  # режим FLYING: движение по вектору

        self.state = Plane.STATE_LANDING
        self.current_route = landing_route
        self.current_index = 1  # следующая цель
        self.speed = speed

        self.servicing_duration = 5  # секундах обслуживания
        self.servicing_start = None

        self.angle = 0  # текущий угол поворота

        self.finished = False  # когда самолёт ушёл за пределы карты

    def update(self):
        # Если самолёт завершил движение, ничего не делаем
        if self.finished:
            return

        # Если состояние - обслуживание, проверяем время
        if self.state == Plane.STATE_SERVICING:
            if time.time() - self.servicing_start >= self.servicing_duration:
                # Переход к взлёту: смена маршрута и состояния
                self.state = Plane.STATE_TAKEOFF
                self.current_route = self.takeoff_route
                self.current_index = 1
                # Обновляем позицию на начало маршрута взлёта
                self.x, self.y = self.current_route[0]
                self.rect.center = (self.x, self.y)
            else:
                # Пока обслуживается – не двигаем, можно добавить мигание или анимацию ожидания
                return

        # Если состояние FLYING – просто двигаем по вектору
        if self.state == Plane.STATE_FLYING:
            self.x += self.flying_vector[0] * self.speed
            self.y += self.flying_vector[1] * self.speed
            self.rect.center = (self.x, self.y)
            # Если улетел за пределы экрана (например, x < -50 или x > ширина), помечаем завершение
            # Здесь можно добавить свою логику проверки
            if self.x < -50 or self.x > 1300 or self.y < -50 or self.y > 800:
                self.finished = True
            self._update_rotation_vector(self.flying_vector)
            self.rotate_image()
            return

        # Для состояний LANDING и TAKEOFF - движение по маршруту
        if self.current_index >= len(self.current_route):
            # Если в режиме LANDING, значит достигли парковки – запускаем обслуживание
            if self.state == Plane.STATE_LANDING:
                self.state = Plane.STATE_SERVICING
                self.servicing_start = time.time()
            # Если в режиме TAKEOFF, значит самолет достиг RW-1 – переходим в FLYING
            elif self.state == Plane.STATE_TAKEOFF:
                self.state = Plane.STATE_FLYING
            return

        target = self.current_route[self.current_index]
        dx = target[0] - self.x
        dy = target[1] - self.y
        distance = math.hypot(dx, dy)

        if distance < self.speed:
            # Прибытие в текущую точку
            self.x, self.y = target
            self.rect.center = (self.x, self.y)
            self.current_index += 1
        else:
            # Движение к цели
            nx = dx / distance
            ny = dy / distance
            self.x += nx * self.speed
            self.y += ny * self.speed
            self.rect.center = (self.x, self.y)
            self._update_rotation_vector((nx, ny))
            self.rotate_image()

    def _update_rotation_vector(self, vec):
        # Рассчитываем угол для поворота: arctan2(-dy, dx) для корректного отображения
        angle_rad = math.atan2(-vec[1], vec[0])
        self.angle = math.degrees(angle_rad)

    def rotate_image(self):
        center = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=center)

    def draw(self, screen):
        if not self.finished:
            screen.blit(self.image, self.rect)
