import pyautogui as pg
from time import sleep

# 4 seconds delay taaki aap target window open kar sako
sleep(4)

file_path = r"Cyber Security\\notes.txt"

try:
    # Best practice: with open() + encoding
    with open(file_path, "r", encoding="utf-8") as file:

        for i, line in enumerate(file, start=1):

            # Empty line skip karne ke liye
            if line.strip():

                print(f"{i}: {line.strip()}")

                # Typing automation
                pg.typewrite(line, interval=0.04)

                # Optional: Enter press
                # pg.press("enter")

except FileNotFoundError:
    print("File not found!")

except UnicodeDecodeError:
    print("Encoding issue! Try another encoding like utf-8-sig.")