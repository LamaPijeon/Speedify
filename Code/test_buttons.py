from gpiozero import Button
import time

prev_btn = Button(5, pull_up=True, bounce_time=0.025)
pause_btn = Button(6, pull_up=True, bounce_time=0.025)
skip_btn = Button(13, pull_up=True, bounce_time=0.025)

prev_btn.when_pressed = lambda: print("PREVIOUS pressed")
pause_btn.when_pressed = lambda: print("PAUSE pressed")
skip_btn.when_pressed = lambda: print("SKIP pressed")

print("Press buttons to test. Ctrl+C to exit.")
while True:
    time.sleep(0.1)
