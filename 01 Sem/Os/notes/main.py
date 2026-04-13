import pyautogui as pg
from time import sleep

sleep(3)
file = open("CAOQuestons.txt","r")
ques = file.read().split("\n")

for que in ques[30:]:
    pg.typewrite(que,0.1)
    sleep(1)
    pg.press("enter")
    sleep(15)