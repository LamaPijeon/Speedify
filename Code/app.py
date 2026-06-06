import time
import threading
from Code.spotify_client import SpotifyClient, TrackFetcher
from Code.display_manager import DisplayManager
from Code.config import DISPLAY_MODE

if DISPLAY_MODE == "screen":
    from Code.server import app

    def run_server():
        app.run(host="0.0.0.0", port=5001)


def main():
    client = SpotifyClient()
    fetcher = TrackFetcher(client.sp)
    display = DisplayManager()
    previous_track = None

    if DISPLAY_MODE == "screen":
        threading.Thread(target=run_server, daemon=True).start()
        print("Preview at http://localhost:5001")

    while True:
        track = fetcher.get_current_track()
        if track != previous_track:
            if track:
                display.render(track)
            else:
                display.clear()
            previous_track = track
        time.sleep(3)


if __name__ == "__main__":
    main()
