import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(8, 6))

color = "#87CEEB"

# 1. Круг (вверху слева)
circle = patches.Circle((1, 5), radius=0.5, facecolor=color, edgecolor='black')
ax.add_patch(circle)

# 2. Маленький квадрат (рядом с кругом)
square1 = patches.Rectangle((2, 4.75), 0.5, 0.5, facecolor=color, edgecolor='black')
ax.add_patch(square1)

# 3. Трапеция (вверху в центре, пошире)
trapezoid_points = [(3, 5.5), (5, 5.5), (4.5, 4.5), (3.5, 4.5)]
trapezoid = patches.Polygon(trapezoid_points, facecolor=color, edgecolor='black')
ax.add_patch(trapezoid)

# 4. Прямоугольник с вырезанным углом (вверху справа)
rect_with_cut_points = [(5, 5.5), (6, 5.5), (6, 4.5), (5.5, 4.5), (5, 5)]
rect_with_cut = patches.Polygon(rect_with_cut_points, facecolor=color, edgecolor='black')
ax.add_patch(rect_with_cut)

# 5. Крест (вверху справа)
cross_points = [
    (6.5, 5.5), (6.7, 5.5), (6.7, 5.3), (6.9, 5.3), (6.9, 5.5), (7.1, 5.5),
    (7.1, 5.1), (6.9, 5.1), (6.9, 4.9), (7.1, 4.9), (7.1, 4.5), (6.9, 4.5),
    (6.9, 4.7), (6.7, 4.7), (6.7, 4.5), (6.5, 4.5), (6.5, 4.9), (6.3, 4.9),
    (6.3, 4.5), (6.1, 4.5), (6.1, 4.9), (6.3, 4.9), (6.3, 5.1), (6.1, 5.1),
    (6.1, 5.5), (6.3, 5.5), (6.3, 5.3), (6.5, 5.3), (6.5, 5.5)
]
cross = patches.Polygon(cross_points, facecolor=color, edgecolor='black')
ax.add_patch(cross)

# 6. Длинный вертикальный прямоугольник (слева внизу)
long_rect = patches.Rectangle((0.5, 1), 0.4, 3, facecolor=color, edgecolor='black')
ax.add_patch(long_rect)

# 7. Горизонтальный прямоугольник (в центре)
horiz_rect = patches.Rectangle((2, 3), 2, 0.5, facecolor=color, edgecolor='black')
ax.add_patch(horiz_rect)

# 8. Прямоугольник с вырезанным углом (справа в центре)
rect_with_cut2_points = [(5, 3.5), (6, 3.5), (6, 2.5), (5.5, 2.5), (5, 3)]
rect_with_cut2 = patches.Polygon(rect_with_cut2_points, facecolor=color, edgecolor='black')
ax.add_patch(rect_with_cut2)

# 9. Пятиугольник (внизу справа)
pentagon_points = [(6, 1.5), (6.5, 2), (7, 1.5), (6.8, 1), (6.2, 1)]
pentagon = patches.Polygon(pentagon_points, facecolor=color, edgecolor='black')
ax.add_patch(pentagon)

# 10. Два квадрата (внизу в центре)
rect2 = patches.Rectangle((2.5, 1), 1, 1, facecolor=color, edgecolor='black')
ax.add_patch(rect2)
rect3 = patches.Rectangle((3.5, 1), 1, 1, facecolor=color, edgecolor='black')
ax.add_patch(rect3)

# Настройка осей
ax.set_xlim(0, 8)
ax.set_ylim(0, 6)
ax.set_aspect('equal')
ax.axis('off')

plt.show()
