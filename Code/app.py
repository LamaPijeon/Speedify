import time
import threading

from spotify_client import SpotifyClient, TrackFetcher
from display_manager import DisplayManager
from config import DISPLAY_MODE

if DISPLAY_MODE == "screen":
    from server import app

    def run_server():
        app.run(host="0.0.0.0", port=5001)


def main():
    display = DisplayManager()

    if DISPLAY_MODE == "еink":
        import os
        flag_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), ".first_boot")

        if not os.path.exists(flag_path):
            display.render_initial(os.path.join(os.path.dirname(
                os.path.abspath(__file__)), "..", "Assets", "Pics", "happy-birthday.png"))
            time.sleep(30)
            open(flag_path, 'w').close()

    while True:
        try:
            client = SpotifyClient()
            fetcher = TrackFetcher(client.sp)
            break
        except Exception as e:
            print(f"Spotify init failed: {e}, retrying in 10s...")
            display.render_random()
            time.sleep(25)

    if DISPLAY_MODE == "eink":
        from button_controller import ButtonController
        buttons = ButtonController(fetcher)

    if DISPLAY_MODE == "screen":
        threading.Thread(target=run_server, daemon=True).start()
        print("Preview at http://localhost:5001")

    previous_track = None
    no_track_start = None
    random_display_start = None
    paused_start = None

    while True:
        track = fetcher.get_current_track()
        paused = False
        if track:
            if hasattr(track, "is_playing"):
                paused = not track.is_playing
            elif isinstance(track, dict):
                paused = not track.get("is_playing", True)

        if track and not paused:
            if random_display_start is not None or track != previous_track:
                display.render(track)
                previous_track = track
            no_track_start = None
            paused_start = None
            random_display_start = None

        elif track and paused:
            if paused_start is None:
                paused_start = time.time()
            elif time.time() - paused_start >= 30:
                if random_display_start is None:
                    display.render_random()
                    random_display_start = time.time()
                    previous_track = None
                elif time.time() - random_display_start >= 120:
                    display.render_random()
                    random_display_start = time.time()

        else:
            paused_start = None
            if previous_track is not None:
                display.clear()
                previous_track = None
            if random_display_start is None:
                if no_track_start is None:
                    no_track_start = time.time()
                elif time.time() - no_track_start >= 30:
                    display.render_random()
                    random_display_start = time.time()
            elif time.time() - random_display_start >= 120:
                display.render_random()
                random_display_start = time.time()

        time.sleep(3)


if __name__ == "__main__":
    main()
