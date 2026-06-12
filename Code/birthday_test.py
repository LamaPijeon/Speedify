from display_manager import DisplayManager
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


display = DisplayManager()
display.render_initial(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "..", "Assets", "Pics", "happy-birthday.png"))
