import pyautogui as pg
from time import sleep

sleep(4)

file = open('Cyber Security/shortNotes.txt','r')
data = file.read()
file.close()

pg.typewrite(data, 0.03)

