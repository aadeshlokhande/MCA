import pyautogui as pg
from time import sleep

sleep(2)

file = open("02 Block Chain Technology\\unit 1.txt")
data = file.read()
# for i in range(200):
#     print(i, file.readline())
file.close()

pg.typewrite(data,0.05)

