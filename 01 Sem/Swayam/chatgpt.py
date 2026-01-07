import pyautogui as pg
from time import sleep
print("<<<<<<<<<<<<< CODE RUN >>>>>>>>>>>>>>>>")
sleep(3)

file = open("Swayam\ImageProcessingPythonTopics.txt", "r",encoding="utf-8")
prompts = file.read().split("\n")

for prompt in prompts:
    pg.typewrite(f"{prompt}",0.06)
    sleep(1)
    # exit()
    pg.press("enter")
    print(f"{prompt} ")
    sleep(10)

