import cv2
import numpy as np
import serial
import colorsys
import time

#Global variables
ser = 0
COMPORT = int(input('Введите номер порта: ')) #Я использовал 1
if __name__ == '__main__':
    def nothing(*arg):
        pass

    #Подключение камеры
    cv2.namedWindow("out_window")
    cap = cv2.VideoCapture(0)

    # Задаем окно и его размер
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    cv2.namedWindow("settings")  # создаем окно настроек

    #Создаем 6 ползунков для диапазона HSV
    cv2.createTrackbar('h1', 'settings', 0, 180, nothing)
    cv2.createTrackbar('s1', 'settings', 0, 255, nothing)
    cv2.createTrackbar('v1', 'settings', 0, 255, nothing)
    cv2.createTrackbar('h2', 'settings', 180, 180, nothing)
    cv2.createTrackbar('s2', 'settings', 255, 255, nothing)
    cv2.createTrackbar('v2', 'settings', 255, 255, nothing)



    while True:
        flag, img = cap.read()#Захват кадра

        height, width = img.shape[:2] #Получаем размеры изображения
        edge = 10

        # Trackbars
        h1 = cv2.getTrackbarPos('h1', 'settings')
        s1 = cv2.getTrackbarPos('s1', 'settings')
        v1 = cv2.getTrackbarPos('v1', 'settings')
        h2 = cv2.getTrackbarPos('h2', 'settings')
        s2 = cv2.getTrackbarPos('s2', 'settings')
        v2 = cv2.getTrackbarPos('v2', 'settings')

        h_min = np.array((h1, s1, v1), np.uint8) #Нижний порог
        h_max = np.array((h2, s2, v2), np.uint8) #Верхний порог
        color_for_import = colorsys.hsv_to_rgb(((h2+h1)/2)/180,((s2+s1)/2)/255,((v2+v1)/2)/255) #Преобразование полученного HSV цвета в RGB

        # Создание массива RGB с преобразованием из процентов в числа
        rgb_color = [round(color_for_import[0]*255,2),round(color_for_import[1]*255,2),round(color_for_import[2]*255,2)]
        print(rgb_color)

        # Соединение по эмулируемому COMPORT'у
        def init_serial():

            global ser  # Must be declared in Each Function
            ser = serial.Serial()
            ser.baudrate = 9600
            ser.port = "COM{}".format(COMPORT)

            ser.timeout = 10
            ser.open()  # Opens SerialPort

            # Открыт порт или закрыт
            #if ser.isOpen():
            #    print('Open: ' + ser.portstr)

        try:
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) #Преобразование из RGB в HSV
            mask = cv2.inRange(img_hsv, h_min, h_max) #Создание маски в диапазоне для поиска кубика

            result = cv2.bitwise_and(img_hsv,img_hsv,mask = mask) #Наложение маски на изображение
            # result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)

            # Поиск моментов для определения координатов центра объекта
            moments = cv2.moments(mask, 1)
            dM01 = moments['m01']
            dM10 = moments['m10']
            dArea = moments['m00']

            x = 0

            if dArea > 200: #Фильтр по Количеству пикселей в области
                x = int(dM10 / dArea)
                y = int(dM01 / dArea)
                cv2.circle(result, (x, y), 3, (255, 0, 0), -1) #Точка, обозначающая центр найденного объекта
                x_coordinate = 'x=' + str(x) + 'px '
                y_coordinate = 'y=' + str(y) + 'px '
                coordinates_out = x_coordinate + y_coordinate
                cv2.putText(img, coordinates_out, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0,255,0), 2)
                init_serial()
                time.sleep(0.2)
                ser.write(str.encode(x_coordinate))
                ser.write(str.encode(y_coordinate))
                ser.write(str.encode(str(rgb_color) + '\r\n'))

                print('You sent: ' + x_coordinate +'; '+y_coordinate)


            cv2.imshow("out_window", img)
            cv2.imshow("result", result)
        except:
            cap.release()
            raise

        ch = cv2.waitKey(50)
        # для выхода надо нажать esc
        if ch == 27:
            break
    cap.release()
    cv2.destroyAllWindows()