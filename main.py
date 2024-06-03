import math
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.image import imread

file_txt = ("/Users/sraperanosan/PycharmProjects/PRIT/test/labels/2R-N-_JPG.rf.18d0e144334d0684c65ba0021f683649.txt")
image= imread("/Users/sraperanosan/PycharmProjects/PRIT/test/images/2R-N-_JPG.rf.18d0e144334d0684c65ba0021f683649.jpg")
coordinates = {}
with open(file_txt, "r") as file:
    for line in file:
        line = line.strip().split()
        class_label = int(line[0])
        # Инвертируем координаты y
        points = [(float(line[i]), float(line[i+1])) for i in range(1, len(line), 2)]
        coordinates.update({class_label: points})

def to_pixel_coordinates(coordinates, image_width, image_height):
    pixel_coordinates = {}
    for class_id, points in coordinates.items():
        pixel_points = []
        for point in points:
            x_pixel = int(point[0] * image_width)
            y_pixel = int(point[1] * image_height)
            pixel_points.append((x_pixel,y_pixel))
        pixel_coordinates[class_id] = pixel_points
    return pixel_coordinates

# Получение размеров изображения
image_height, image_width, _ = image.shape

pixel_coordinates = to_pixel_coordinates(coordinates, image_width, image_height)
plt.imshow(image)

# Отображаем только самые нижние точки
lowest_points = [max(points, key=lambda p: p[1]) for points in pixel_coordinates.values()]

# Извлекаем координаты X и Y для каждой точки
x_coords = [point[0] for point in lowest_points]
y_coords = [point[1] for point in lowest_points]

a=(x_coords[0],y_coords[0])
b=(x_coords[1],y_coords[1])
c=(x_coords[2],y_coords[2])

# returns square of distance b/w two points
def lengthSquare(X, Y):
    xDiff = X[0] - Y[0]
    yDiff = X[1] - Y[1]
    return xDiff * xDiff + yDiff * yDiff

def printAngle(A, B, C):
    # Square of lengths be a2, b2, c2
    a2 = lengthSquare(B, C)
    b2 = lengthSquare(A, C)
    c2 = lengthSquare(A, B)

    # length of sides be a, b, c
    a = math.sqrt(a2)
    b = math.sqrt(b2)
    c = math.sqrt(c2)

    # From Cosine law
    alpha = math.acos((b2 + c2 - a2) / (2 * b * c))
    betta = math.acos((a2 + c2 - b2) / (2 * a * c))
    gamma = math.acos((a2 + b2 - c2) / (2 * a * b))

    # Converting to degree
    alpha = alpha * 180 / math.pi
    betta = betta * 180 / math.pi
    gamma = gamma * 180 / math.pi

    # printing all the angles
    print("alpha : %f" % (alpha))
    print("betta : %f" % (betta))
    print("gamma : %f" % (gamma))
    return betta

angle = printAngle(a, b, c)

# Радиус окружности
radius = 30

# Создаем массив углов для построения окружности
theta = np.linspace(0, 2*np.pi, 100)

# Вычисляем координаты точек окружности
x_circle = b[0] + radius * np.cos(theta)
y_circle = b[1] + radius * np.sin(theta)

text = ""
if(angle <= 130): text = "Нормальная стопа"
elif(angle >= 131 and angle <= 140): text = "Первая степень плоскостопия"
elif(angle >= 141 and angle <= 155): text = "Вторая степень плоскостопия"
elif(angle > 155): text = "Третья степень плоскостопия"

plt.plot(x_circle, y_circle, color='green', label=f'Окружность, угол: {angle:.2f} градусов')
plt.plot(x_coords + [x_coords[0]], y_coords + [y_coords[0]], color='blue')



# Добавляем точку b

# Отображаем только самые нижние точки
plt.scatter(x_coords, y_coords, color='red', label='Самые нижние точки')

# Добавляем легенду и метки осей
plt.legend()
plt.xlabel('X')
plt.ylabel('Y')
plt.title(text)

plt.grid(True)

# Показываем график
plt.show()
