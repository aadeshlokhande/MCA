import pyautogui as pg
from time import sleep

sleep(4)
file_path = "AI\\AI Notes.txt"
try:
    with open(file_path, "r", encoding="utf-8") as file:
        for i, line in enumerate(file, start=1):
            if line.strip():
                pg.typewrite(line, interval=0.04)

except FileNotFoundError:
    print("File not found!")
except UnicodeDecodeError:
    print("Encoding issue! Try another encoding like utf-8-sig.")