import cv2
import numpy as np

# Создаем объект для чтения видеопотока
cap = cv2.VideoCapture(0)

# Определяем границы цветового диапазона кожи
lower_skin = np.array([115, 0, 0], dtype=np.uint8)
upper_skin = np.array([180, 255, 255], dtype=np.uint8)


while True:
    # Считываем кадр видеопотока
    ret, frame = cap.read()
    #frame = cv2.imread('imgs/3.jpg')
    # Преобразуем изображение в цветовое пространство HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Применяем маску для выделения области с цветом кожи
    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # Удаляем шум с помощью морфологических операций
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=1)

    # Находим контуры на изображении
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Находим контур с максимальной площадью (предполагается, что это рука)
    if len(contours) > 0:
        max_contour = max(contours, key=cv2.contourArea)
        for cont in contours:
            if len(cont) > 18:
                rect = cv2.minAreaRect(cont)  # пытаемся вписать прямоугольник
                box = cv2.boxPoints(rect)  # поиск четырех вершин прямоугольника
                box = np.int0(box)  # округление координат
                cv2.drawContours(frame, [box], 0, (255, 0, 0), 2)  # рисуем прямоугольник
        # Извлекаем признаки для классификации жестов руки
        x, y, w, h = cv2.boundingRect(max_contour)
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3)
        if w > 150 and w < 250:
            result = "figers together"
        elif w <= 150:
            result = "V fingers"
        else:
            result = "fingers splashed"
        cv2.putText(frame, str('Gesture: ' + result), (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    # Отображаем кадр видеопотока
    cv2.imshow('Hand Gesture Recognition', frame)

    # Выход по нажатию клавиши 'q'
    if cv2.waitKey(1) and 0xFF == ord("q"):
        break