# Примеры работы с YOLO моделями
___
### Поиск ключевых точек тела - определения позы человека

Пойдём по блокам базового кода, где будем объяснять всё что происходит

```python
from ultralytics import YOLO
import cv2
import numpy as np
import os

model = YOLO('yolov8n-pose.pt')
```

Тут происходит импортирование библиотек, а так же загружается уже предобученная модель `yolov8n-pose.pt` (n – nano, самая лёгкая). Она способна находить людей и их 17 ключевых точек (поза COCO).
___
```python
colors = {
    'white': (255, 255, 255),
    'red': (0, 0, 255),
    'blue': (255, 0, 0)
}
```

Удобно заданы три цвета в формате BGR (OpenCV использует BGR, а не RGB). Они будут использоваться для отрисовки разных частей скелета: руки – белым, ноги – красным, туловище – синим, точки – синим.
___
```python
def draw_skeleton(image, keypoints, confs, pairs, color):
    for (start, end) in pairs:
        if confs[start] > 0.5 and confs[end] > 0.5:
            x1, y1 = int(keypoints[start][0]), int(keypoints[start][1])
            x2, y2 = int(keypoints[end][0]), int(keypoints[end][1])
            if (x1, y1) != (0, 0) and (x2, y2) != (0, 0):
                cv2.line(image, (x1, y1), (x2, y2), color, 2)
```

Тут рисуем линии скелета, кости, между парами ключевых точек. 
- `keypoints`: массив координат ключевых точек (одна персона) размером `(17, 2)` (x, y).
- `confs`: массив уверенностей для каждой точки размером `(17,)`.
- `pairs`: список кортежей `(start, end)` – индексы точек, которые нужно соединить.
- `color`: цвет линии.
Для каждой пары проверяется, что уверенность обеих точек больше 0.5 - иначе линия не рисуется (маловероятная точка). Далее координаты преобразуются в целые числа. Дополнительно проверяется, что точка не равно (0, 0). Это стандартное значение YOLO для невидимой точки, мы её таким образом игнорируем, далее рисуется сама линия вызовом `cv2.line`
___
Далее поговорим об основной функции, которая выполняет всю работу для одного изображения.

```python
def process_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print("Ошибка: не удалось загрузить изображение")
        return
    results = model(image)[0]
```

Сначала считываем картинку с диска, если файл битый или путь неверный, то выводим ошибку, база. Далее (последняя строка), запускаем модель на изображении. Так `model(image)` возвращает список (обычно из одного элемента, так как одно изображение). Берём нулевой элемент – это объект `Results`, содержащий всю информацию: боксы, ключевые точки, классы.
___
```python

if hasattr(results, 'boxes') and hasattr(results.boxes, 'cls') and len(results.boxes.cls) > 0:
        classes_names = results.names          # словарь {0: 'person', ...} (для COCO)
        classes = results.boxes.cls.cpu().numpy()   # массив классов объектов
        boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)  # координаты боксов
```
Сначала в if идёт небольшая проверка, есть ли вообще найденные объекты. Если нет, то дальнейшая отрисовка не требуется. Далее извлекаем именная классов, индексов и б-боксы. Переносим на CPU и конвертируем в NumPy
___
```python
if results.keypoints:
    keypoints = results.keypoints.data.cpu().numpy()   # (N, 17, 2)
    confs = results.keypoints.conf.cpu().numpy()       # (N, 17) уверенности
```
Если модель вернула ключевые точки (то есть объект есть на изображении), забираем массивы координат и уверенностей. Размерность будет: N - кол-во людей, 17 - кол-во точек на человеке.
___
```python
for i, (class_id, box, kp, conf) in enumerate(zip(classes, boxes, keypoints, confs)):
```
Тут мы перебираем одновременно класс, б-бокс, ключевые точки и их уверенность для КАЖДОГО НАЙДЕННОГО объекта на изображении, если людей несколько допустим, мы переберём каждого из них.
___
```python
draw_box=False
    if draw_box:
        class_name = classes_names[int(class_id)]
        color = colors['white']
        x1, y1, x2, y2 = box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
```

Тут блок рисования б-бокса (если надо). Флаг `draw_box=False` означает, что отрисовка блоком отключена. Но если нужна то происходит следующее: Забираем название класса объекта, далее определяем цвет самого б-бокса, забираем координаты из б-бокса по нашему объекту (мы ранее как раз перебираем объекты и вот щас допустим мы на одном из людей). Далее при помощи `cv2.rectangle` рисуем сам прямоугольник по нужным нам координатам и с нужным нам цветом. Далее помещаем название объекта на y1 - 10 позицию бокса. 
___
```python
for j, (point, point_conf) in enumerate(zip(kp, conf)):
    if point_conf > 0.5:
        x, y = int(point[0]), int(point[1])
        if (x, y) != (0, 0):
            cv2.circle(image, (x, y), 5, colors['blue'], -1)
            cv2.putText(image, str(j), (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['blue'], 2)

```

Тут происходит отрисовка ключевых точек с номерами, а именно: Для каждой из 17 точек проверяется из уверенность, если она выше 0.5 и координаты не (0, 0), то рисуем синий кружок радиусом 5 пикселей, а рядом выводим номер точки (индекс) синим текстом.
___
```python
draw_skeleton(image, kp, conf, [(5, 7), (7, 9), (6, 8), (8, 10)], colors['white']) # Руки

draw_skeleton(image, kp, conf, [(11, 13), (13, 15), (12, 14), (14, 16)], colors['red']) # Ноги

draw_skeleton(image, kp, conf, [(5, 11), (6, 12)], colors['blue']) # Тело
```
Тут уже происходит соединение наших точек, вызываем ранее написанную функцию, где мы проверяли уверенность точек вновь, координаты и объединяли их. Важно заметить, что для каждой части тела вызываются свои функции со своими точками, а именно 

- **Руки (белые):** левое плечо (5) → левый локоть (7) → левое запястье (9); правое плечо (6) → правый локоть (8) → правое запястье (10).
- **Ноги (красные):** левое бедро (11) → левое колено (13) → левая щиколотка (15); аналогично для правой стороны.
- **Тело (синие):** левое плечо (5) → левое бедро (11); правое плечо (6) → правое бедро (12). Это создаёт две линии по бокам туловища.

Использование трёх цветов помогает визуально отделить части тела.
Пары точек тоже берутся не из неоткуда, а именно, это важно знать. Стандарт COCO для 17 ключевых точек. YOLOv8‑pose (как и почти все современные pose estimation модели) обучалась на датасете **COCO**. В нём каждая точка тела человека имеет фиксированный индекс от 0 до 16. Именно эти индексы и используются в коде.

| Индекс | Часть тела       |
| ------ | ---------------- |
| 0      | Нос              |
| 1      | Левый глаз       |
| 2      | Правый глаз      |
| 3      | Левое ухо        |
| 4      | Правое ухо       |
| 5      | Левое плечо      |
| 6      | Правое плечо     |
| 7      | Левый локоть     |
| 8      | Правый локость   |
| 9      | Левое запястье   |
| 10     | правое запястье  |
| 11     | Левое бедро      |
| 12     | Правое бедро     |
| 13     | Левое колено     |
| 14     | правое колено    |
| 15     | Левая щиколотка  |
| 16     | Правая щиколотка |
___
```python
output_path = os.path.splitext(image_path)[0] + "_pose_detected.jpg"
cv2.imwrite(output_path, image)
print(f"Сохранено изображение с результатами: {output_path}")

cv2.imshow('YOLOv8-Pose Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

Тут происходит сохранение и отображение результат. Формируется image_path , убирается расширение, добавляется суффикс `_pose_detected.jpg`. Показывается в окне OpenCV. `waitKey(0)` ждёт нажатия любой клавиши, затем окно закрывается.


___
#### Полный код
```python
from ultralytics import YOLO
import cv2
import numpy as np
import os

# Загрузка модели YOLOv8-Pose (nano-версия)
model = YOLO('yolov8n-pose.pt')

# Цвета для разных частей скелета (BGR)
colors = {
    'white': (255, 255, 255),
    'red': (0, 0, 255),
    'blue': (255, 0, 0)
}

def draw_skeleton(image, keypoints, confs, pairs, color):
    """Рисует линии скелета между заданными парами ключевых точек."""
    for (start, end) in pairs:
        if confs[start] > 0.5 and confs[end] > 0.5:
            x1, y1 = int(keypoints[start][0]), int(keypoints[start][1])
            x2, y2 = int(keypoints[end][0]), int(keypoints[end][1])
            if (x1, y1) != (0, 0) and (x2, y2) != (0, 0):
                cv2.line(image, (x1, y1), (x2, y2), color, 2)

def process_image(image_path):
    """Основная функция: загрузка, детекция, отрисовка и сохранение результата."""
    image = cv2.imread(image_path)
    if image is None:
        print("Ошибка: не удалось загрузить изображение")
        return

    results = model(image)[0]

    if hasattr(results, 'boxes') and hasattr(results.boxes, 'cls') and len(results.boxes.cls) > 0:
        classes_names = results.names
        classes = results.boxes.cls.cpu().numpy()
        boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)

        if results.keypoints:
            keypoints = results.keypoints.data.cpu().numpy()
            confs = results.keypoints.conf.cpu().numpy()

            for i, (class_id, box, kp, conf) in enumerate(zip(classes, boxes, keypoints, confs)):
                # Отрисовка bounding box (отключена)
                draw_box = False
                if draw_box:
                    class_name = classes_names[int(class_id)]
                    x1, y1, x2, y2 = box
                    cv2.rectangle(image, (x1, y1), (x2, y2), colors['white'], 2)
                    cv2.putText(image, class_name, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['white'], 2)

                # Ключевые точки и их номера
                for j, (point, point_conf) in enumerate(zip(kp, conf)):
                    if point_conf > 0.5:
                        x, y = int(point[0]), int(point[1])
                        if (x, y) != (0, 0):
                            cv2.circle(image, (x, y), 5, colors['blue'], -1)
                            cv2.putText(image, str(j), (x + 5, y - 5),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['blue'], 2)

                # Рисование скелета (руки, ноги, туловище)
                draw_skeleton(image, kp, conf, [(5, 7), (7, 9), (6, 8), (8, 10)], colors['white'])  # Руки
                draw_skeleton(image, kp, conf, [(11, 13), (13, 15), (12, 14), (14, 16)], colors['red'])  # Ноги
                draw_skeleton(image, kp, conf, [(5, 11), (6, 12)], colors['blue'])  # Тело

    output_path = os.path.splitext(image_path)[0] + "_pose_detected.jpg"
    cv2.imwrite(output_path, image)
    print(f"Сохранено изображение с результатами: {output_path}")

    cv2.imshow('YOLOv8-Pose Detection', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Обработка конкретного изображения
image_path = 'd.jpg'
process_image(image_path)
```