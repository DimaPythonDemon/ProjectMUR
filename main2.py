import pymurapi as mur
import cv2
import time
import numpy as np

def clamp(v, min, max):
    if v < min:
        return min
    if v > max:
        return max
    return v

commands = {"ignore": 15, "recognize": True, 
            "color_start": (0, 0, 0),
            "color_finish": (27, 255, 255)}

auv = mur.mur_init()

class Controller():
    
    def log_depth(self):
        print(["зелёный цвет", "синий цвет", "фиолетовый цвет"][int(self.auv.get_depth() > 3)])
    
    def keep_depth(self, depth_to_set):
        cur_depth = self.auv.get_depth()
        motor = 80 * (cur_depth - depth_to_set)    
        self.auv.set_motor_power(3, clamp(int(motor), -100, 100))
        self.auv.set_motor_power(2, clamp(int(motor), -100, 100))
        color_rgb = (0, 0, 0)
        # if cur_depth > 3: self.flag = False
        self.log_depth()
    
    def swap_yaw(self, degree=0):
        yaw = self.auv.get_yaw()
        recalculated_yaw = yaw if (0 <= yaw <= 180) else 360 + yaw
        motor = 70 * (recalculated_yaw - degree)
        self.auv.set_motor_power(1, clamp(int(motor), -100, 100))
        print("povorot")

    def move_toward(self, power=0):
        self.auv.set_motor_power(1, power)
        self.auv.set_motor_power(0, power)
        
    def controlling(self):
        if self.status == 0:
            print("ghj")
            self.keep_depth(self.needed_depth)
        elif self.status == 1:
            self.move_toward(power=self.power)
            self.log_depth()
        elif self.status == 2:
            self.swap_yaw(degree=self.degree)
    
    def __init__(self, auv, commands):
        self.commands = commands
        self.auv = auv
        self.needed_depth = 1
        self.stop = False
        self.status = 0
        self.previous_time = 0
        self.power = 0
        self.degree = 0
        
    def recognize(self, video=False, param=False) -> str:
        # Создаем объект для чтения видеопотока
        cap = video

        # Определяем границы цветового диапазона кожи
        lower_skin = np.array([115, 0, 0], dtype=np.uint8)
        upper_skin = np.array([180, 255, 255], dtype=np.uint8)


        # Считываем кадр видеопотока
        ret, frame = cap.read()
        # frame = cv2.imread('imgs/3.jpg')
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
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            result = ''
            if w > 150 and w < 250:
                result = "figers together"
            elif w <= 150:
                result = "V fingers"
            else:
                result = "fingers splashed"
            cv2.putText(frame, str('Gesture: ' + result), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow(winname="fffff", mat=frame)
        if param:
            cv2.imwrite(frame, 'imgs/imaage.jpg')

        return str(["figers together", "V fingers", "fingers splashed"].index(result))

            
    def main(self):
        if self.commands:
            print("commands loaded")
            video = cv2.VideoCapture(0)
            while not self.stop:
                self.controlling()
                if int(time.time() * 1000) - self.previous_time > 500:
                    '''try:'''
                    with open("settings.txt", "r") as file:
                        text = list(map(int, file.readline().split()))
                        self.status = text[0]
                        if self.status == 0:
                            self.needed_depth = text[1]
                        elif self.status == 1:
                            self.power = text[1]
                        elif self.status == 2:
                            self.degree = text[1]
                        elif self.status == 3:
                            res = self.recognize(video=video)
                            if res == 2:
                                self.auv.set_rgb_color(255, 0, 0)
                                self.stop = True
                            elif res == 1:
                                self.auv.set_rgb_color(0, 255, 0)
                            else:
                                self.auv.set_rgb_color(0, 0, 255)
                            print(res)

                    '''except Exception as err:
                        print(err)'''

            self.stop = False
            while not self.stop:
                if int(time.time() * 1000) - self.previous_time > 500:
                    self.needed_depth = 1
                    self.status = 0
                    self.auv.set_rgb_color(0, 0, 255)
                    self.controlling()
                    self.recognize(video, param=True)



if __name__ == "__main__":
    control = Controller(auv, commands)
    control.main()
    print("task completed")
   
