# Transfer Learning — дообучение готовых сетей

## Зачем дообучать, а не создавать с нуля

Обучить CNN с нуля — дорого. ResNet-50 требует ~8 дней на 8 GPU для ImageNet (1.2 млн картинок). У вас столько данных нет, да и ждать неделю не хочется.

**Transfer Learning (дообучение)** — берём сеть, которая уже обучена на огромном датасете (ImageNet — 1000 классов, 1.2 млн картинок), и дообучаем её под свою задачу.

**Почему это работает:** первые слои CNN учатся находить базовые признаки: линии, границы, текстуры. Они универсальны — кошки, машины или столы состоят из одних и тех же линий и границ. Только последние слои настраиваются под конкретные классы. Поэтому мы можем взять "базу" из первых слоёв и переучить только верхушку.

### Три сценария дообучения

**Сценарий 1: мало данных, похожие классы**
Допустим, у вас 500 картинок кошек и собак. ImageNet уже умеет различать кошек и собак. Просто заменяем последний слой — и сеть почти готова:

```python
import torchvision.models as models

# Загружаем предобученный ResNet
model = models.resnet18(pretrained=True)

# Замораживаем все слои — они уже обучены
for param in model.parameters():
    param.requires_grad = False

# Заменяем последний слой (классификатор) под нашу задачу
# У ResNet последний слой — model.fc (fully connected)
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, 2)  # 2 класса: кошки и собаки

# Обучаем только последний слой
optimizer = torch.optim.Adam(model.fc.parameters(), lr=0.001)
```

**Сценарий 2: много данных, похожие классы**
У вас 50 000 картинок кошек и собак. Больше данных — можно разморозить больше слоёв:

```python
model = models.resnet18(pretrained=True)

# Замораживаем только первые блоки
# Слой за слоем решаем, что разморозить
for name, param in model.named_parameters():
    if 'layer1' in name or 'layer2' in name:
        param.requires_grad = False
    else:
        param.requires_grad = True

# Или размораживаем всё и обучаем с маленьким lr
for param in model.parameters():
    param.requires_grad = True

model.fc = nn.Linear(512, 2)
optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)  # lr в 10 раз меньше
```

**Сценарий 3: мало данных, совсем другие классы**
У вас 200 картинков рентгеновских снимков (медицина). ImageNet не видел ничего похожего. Лучше не замораживать первые слои, а дообучать всю сеть, но с маленьким lr, или использовать Feature Extraction (просто взять признаки, не обучая):

```python
# Feature Extraction — просто берём "отпечатки" (embeddings)
model = models.resnet18(pretrained=True)
model.fc = nn.Identity()  # убираем классификатор, оставляем только признаки

# Пропускаем все картинки через сеть один раз
features = []
with torch.no_grad():
    for images, labels in dataloader:
        emb = model(images)  # получаем векторы-признаки
        features.append(emb)

# Обучаем простой классификатор поверх признаков
from sklearn.svm import SVC
classifier = SVC().fit(torch.cat(features), all_labels)
```

---

## Популярные архитектуры CNN

### ResNet (2015) — ResNet-18, ResNet-50, ResNet-101

**Главная идея:** residual connection (остаточная связь, shortcut connection). Проблема глубоких сетей (VGG с 19 слоями и больше) — градиент затухает, сеть не обучается. ResNet добавил "прыжки" через слои: вход суммируется с выходом блока.

```
Обычный блок:          Residual блок:
x → Conv → ReLU → Conv → ReLU    x → Conv → ReLU → Conv → + → ReLU
                                                          ↑
                                                          └── x (shortcut)
```

![[Pasted image 20260625104540.png]]

**Почему это работает:** градиент может "проскочить" через shortcut прямо к ранним слоям, не затухая. Поэтому ResNet можно делать на 50, 101 и даже 152 слоя — все обучаются.

```python
# ResNet-18 — лёгкий, быстрый, хорош для маленьких датасетов
model = models.resnet18(pretrained=True)   # 11 млн параметров
# Вход: 224×224, выход: 1000 классов (ImageNet)

# ResNet-50 — золотая середина
model = models.resnet50(pretrained=True)   # 25 млн параметров

# ResNet-101 — тяжёлый, для серьёзных задач
model = models.resnet101(pretrained=True)  # 44 млн параметров
```

**Структура ResNet-18:**
```
7×7 Conv, 64 → MaxPool → Layer1: 2 блока × 64 канала
                        → Layer2: 2 блока × 128 каналов
                        → Layer3: 2 блока × 256 каналов
                        → Layer4: 2 блока × 512 каналов
                        → AvgPool → FC (512 → 1000)
```

Последний слой называется `model.fc`. При дообучении заменяем его:

```python
model.fc = nn.Linear(512, num_classes)   # ResNet-18
model.fc = nn.Linear(2048, num_classes)  # ResNet-50 (у него 2048, не 512)
```

**Когда выбирать:**
- ResNet-18: маленькие датасеты (< 10 000), быстрый эксперимент
- ResNet-50: стандартный выбор для большинства задач
- ResNet-101: большие датасеты, высокая точность, есть GPU

---

### VGG (2014) — VGG-16, VGG-19

**Главная идея:** очень простая и однородная архитектура. Только Conv 3×3, MaxPool 2×2, и полносвязные слои в конце. Никаких хитростей. Просто много слоёв подряд.

```python
model = models.vgg16(pretrained=True)   # 138 млн параметров!
model = models.vgg19(pretrained=True)   # 143 млн параметров
```

**Структура VGG-16:**
```
Conv3-64 → Conv3-64 → MaxPool
Conv3-128 → Conv3-128 → MaxPool
Conv3-256 → Conv3-256 → Conv3-256 → MaxPool
Conv3-512 → Conv3-512 → Conv3-512 → MaxPool
Conv3-512 → Conv3-512 → Conv3-512 → MaxPool
FC-4096 → FC-4096 → FC-1000
```

**Недостатки:**
- 138 млн параметров — очень много (ResNet-18: 11 млн)
- 3 полносвязных слоя по 4096 нейронов — ~100 млн параметров только в классификаторе
- Тяжёлая, медленная
- Сегодня почти не используется для задач, где важна скорость

**Когда выбирать:**
- Когда точность важнее скорости
- Учебные задачи (архитектура очень понятная)
- Feature Extraction (средние слои VGG дают качественные признаки)

```python
# У VGG классификатор — model.classifier (не .fc!)
model = models.vgg16(pretrained=True)

for param in model.parameters():
    param.requires_grad = False

# Последний слой — model.classifier[6]
num_features = model.classifier[6].in_features
model.classifier[6] = nn.Linear(num_features, num_classes)
```

---

### MobileNet (2017) — MobileNetV2, MobileNetV3

**Главная идея:** максимальная эффективность для мобильных устройств. Использует depthwise separable convolution — разбивает обычную свёртку на две: сначала свёртка в каждом канале отдельно (depthwise), потом смешивание каналов (pointwise — 1×1).

```
Обычная свёртка: 3×3 × 3 канала × 16 выходов = 432 операции
Depthwise:       3×3 × 3 канала = 27 операций (каждый канал отдельно)
Pointwise (1×1): 1×1 × 3 канала × 16 выходов = 48 операций
Итого: 75 операций вместо 432 — в 5.7 раз меньше!
```

```python
model = models.mobilenet_v2(pretrained=True)   # 3.5 млн параметров
model = models.mobilenet_v3_small(pretrained=True)  # 2.5 млн
model = models.mobilenet_v3_large(pretrained=True)  # 5.4 млн
```

**Когда выбирать:**
- Когда скорость важнее точности (мобильные приложения, real-time)
- Ограниченные ресурсы (CPU, маленькая память)
- MobileNetV3 Large близок к ResNet-50 по точности, но в разы быстрее

```python
# У MobileNetV2 последний слой — model.classifier
model = models.mobilenet_v2(pretrained=True)
model.classifier[1] = nn.Linear(model.last_channel, num_classes)

# У MobileNetV3 — тоже model.classifier
model = models.mobilenet_v3_large(pretrained=True)
model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
```

---

### EfficientNet (2019)

**Главная идея:** ищет оптимальное соотношение между глубиной, шириной и разрешением сети через compound scaling. Авторы показали: если хотите увеличить сеть, нужно одновременно увеличивать и глубину, и ширину, и размер входа, а не что-то одно.

```python
model = models.efficientnet_b0(pretrained=True)   # 5.3 млн, точнее MobileNet
model = models.efficientnet_b3(pretrained=True)   # 12 млн, точнее ResNet-50
model = models.efficientnet_b7(pretrained=True)   # 66 млн, SOTA по точности
```

**Когда выбирать:**
- Когда нужна лучшая точность при заданных ресурсах
- B0 — хорош для маленьких датасетов
- B3-B5 — для серьёзных задач

```python
# EfficientNet: последний слой — model.classifier
model = models.efficientnet_b0(pretrained=True)
num_features = model.classifier[1].in_features
model.classifier[1] = nn.Linear(num_features, num_classes)
```

---

### DenseNet (2017)

**Главная идея:** каждый слой получает на вход выходы ВСЕХ предыдущих слоёв (concat, а не sum, как ResNet). Это максимальное использование информации — градиенты легко доходят до самых ранних слоёв.

```python
model = models.densenet121(pretrained=True)  # 8 млн параметров
model = models.densenet201(pretrained=True)  # 20 млн
```

**Плюсы:** меньше параметров, чем ResNet, при сопоставимой точности, нет проблемы затухания градиентов.
**Минусы:** требует больше памяти (хранить карты признаков всех предыдущих слоёв).

```python
# DenseNet: последний слой — model.classifier
model = models.densenet121(pretrained=True)
model.classifier = nn.Linear(model.classifier.in_features, num_classes)
```

---

## Какой размер картинок ожидает сеть

Все сети из torchvision.trainmodels ожидают на вход картинки 224×224 (кроме некоторых версий). Нужно ресайзить:

```python
from torchvision import transforms

preprocess = transforms.Compose([
    transforms.Resize(256),          # сначала до 256
    transforms.CenterCrop(224),      # потом обрезать центр 224×224
    transforms.ToTensor(),
    transforms.Normalize(            # нормировка как при обучении на ImageNet
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])
```

**Почему такие mean и std?** Это средние и стандартные отклонения пикселей по всему ImageNet. Все предобученные сети обучены с этой нормализацией. Если вы подадите картинку без неё — распределение пикселей будет совершенно другим, и сеть будет работать плохо.

---

## Сравнение архитектур

| Архитектура | Параметры | Размер | ImageNet Acc | Когда брать |
|------------|-----------|--------|--------------|-------------|
| MobileNetV3 Small | 2.5 млн | 6 MB | 67% | Телефон, CPU, real-time |
| MobileNetV3 Large | 5.4 млн | 14 MB | 75% | Быстрая, но точная |
| ResNet-18 | 11 млн | 44 MB | 70% | Стартовая точка, мало данных |
| EfficientNet-B0 | 5.3 млн | 20 MB | 77% | Лучшее соотношение скорость/точность |
| DenseNet-121 | 8 млн | 30 MB | 74% | Точный, меньше параметров |
| ResNet-50 | 25 млн | 98 MB | 76% | Стандартный выбор |
| EfficientNet-B3 | 12 млн | 47 MB | 81% | Когда точность важна |
| VGG-16 | 138 млн | 528 MB | 71% | Учебные задачи |
| ResNet-101 | 44 млн | 170 MB | 78% | Большие датасеты |

---

## Полный шаблон дообучения

```python
import torch
import torch.nn as nn
import torchvision.models as models
from torchvision import transforms, datasets
from torch.utils.data import DataLoader

# 1. Подготовка данных
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.RandomHorizontalFlip(),   # аугментация
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

train_data = datasets.ImageFolder("data/train", transform=transform)
val_data = datasets.ImageFolder("data/val", transform=transform)
train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
val_loader = DataLoader(val_data, batch_size=32)

# 2. Загрузка предобученной модели
model = models.resnet18(pretrained=True)

# 3. Заморозка всех слоёв, кроме последнего
for param in model.parameters():
    param.requires_grad = False

# 4. Замена последнего слоя
num_features = model.fc.in_features
model.fc = nn.Sequential(
    nn.Linear(num_features, 256),
    nn.ReLU(),
    nn.Dropout(0.5),
    nn.Linear(256, len(train_data.classes))
)

# 5. Оптимизатор (только для незамороженных параметров)
optimizer = torch.optim.Adam(model.fc.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

# 6. Обучение
for epoch in range(10):
    model.train()
    for images, labels in train_loader:
        pred = model(images)
        loss = criterion(pred, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # Валидация
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in val_loader:
            pred = model(images)
            _, predicted = pred.max(1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    print(f"Epoch {epoch}: val_acc = {100 * correct / total:.2f}%")
```

**Когда разморозить все слои.** Если после 5-10 эпох accuracy перестала расти, можно разморозить все слои и продолжить с маленьким lr:

```python
# Размораживаем всё
for param in model.parameters():
    param.requires_grad = True

# Новый оптимизатор с маленьким lr
optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)

# Обучаем ещё 10-20 эпох
```

---

## Советы по дообучению

1. **Всегда начинайте с заморозки.** Обучите только новый классификатор 5-10 эпох. Потом если точность не растёт — разморозьте и дообучите всё.

2. **Learning rate для дообучения.** Для замороженной сети — 0.001 (как обычно). Для полного дообучения — 0.0001 (в 10 раз меньше). Если lr слишком большой — предобученные веса "сломаются".

3. **Аугментация критична.** На маленьких датасетах без аугментации моментально переобучение. Хотя бы RandomHorizontalFlip и RandomRotation.

4. **Размер батча.** Чем больше — тем лучше для BatchNorm (который в каждой сети). 32 — минимум.

5. **Если classes отличаются от ImageNet.** ImageNet не видел рентгенов. Первые слои всё ещё полезны (линии, границы), но дообучать придётся всю сеть.

6. **Не используйте VGG если не нужно.** ResNet-18 легче в 10 раз и даёт ту же точность.