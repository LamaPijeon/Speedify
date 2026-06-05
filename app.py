import time
import threading
import os
from spotify_client import SpotifyClient, TrackFetcher
from display_manager import DisplayManager
from server import app


def run_server():
    app.run(host="0.0.0.0", port=5001)


def main():
    client = SpotifyClient()
    fetcher = TrackFetcher(client.sp)
    display = DisplayManager()
    previous_track = None

    threading.Thread(target=run_server, daemon=True).start()
    print("Preview at http://localhost:5001")

    i = 0
    while i < 4:
        track = fetcher.get_current_track()
        if track != previous_track:
            if track:
                display.render(track)
            else:
                display.clear()
            previous_track = track
        time.sleep(3)
        i += 1


if __name__ == "__main__":
    main()
