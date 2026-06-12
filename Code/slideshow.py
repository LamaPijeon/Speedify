from display_manager import DisplayManager
import time
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    display = DisplayManager()
    while True:
        display.render_random()
        time.sleep(20)


if __name__ == "__main__":
    main()
