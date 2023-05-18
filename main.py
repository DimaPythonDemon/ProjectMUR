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
        
    def recognize(self, video=False):
        if not video:
            video = cv2.VideoCapture(0)
        status, img = video.read()

        hsv_min = np.array((0, 54, 5), np.uint8)
        hsv_max = np.array((187, 255, 253), np.uint8)

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # меняем цветовую модель с BGR на HSV
        thresh = cv2.inRange(hsv, hsv_min, hsv_max)  # применяем цветовой фильтр
        _, contours0, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # перебираем все найденные контуры в цикле
        for cnt in contours0:
            rect = cv2.minAreaRect(cnt)  # пытаемся вписать прямоугольник
            box = cv2.boxPoints(rect)  # поиск четырех вершин прямоугольника
            box = np.int0(box)  # округление координат
            cv2.drawContours(img, [box], 0, (255, 0, 0), 2)  # рисуем прямоугольник

        cv2.imshow('contours', img)  # вывод обработанного кадра в окно

        cv2.waitKey()
        cv2.destroyAllWindows()

        '''if status:
            
            csv_draw = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV)
            img_mask = cv2.inRange(csv_draw, 
                                   self.commands['color_start'],
                                   self.commands['color_finish'])
                                   
                                  
            im = image.copy()
            imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            ret, thresh = cv2.threshold(imgray, 150, 255, 0)
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(im, contours, -1, (0,255,0), 3)
            
            cv2.imshow("cam 1", im)
            cv2.waitKey(50)'''
            
    def main(self):
        if self.commands:
            print("commands loaded")
            # video = cv2.VideoCapture(0)
            while not self.stop:
                self.controlling()
                if int(time.time() * 1000) - self.previous_time > 500:
                    try:
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
                                self.recognize()
                    except Exception as err:
                        print(err)

if __name__ == "__main__":
    control = Controller(auv, commands)
    control.main()
    print("task completed")
    
    
    
    
    
    
    
    
