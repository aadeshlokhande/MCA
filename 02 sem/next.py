from time import sleep
import pyautogui as pg

sleep(3)

for i in range(12):
    pg.typewrite("next", 0.2)
    pg.press("enter")
    sleep(7)

