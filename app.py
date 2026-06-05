import time
import os
from spotify_client import SpotifyClient, TrackFetcher
from display_manager import DisplayManager
from waveshare_epd import epd3in6e


def main():

    epd = epd3in6e.EPD()
    epd.init()
    epd.Clear()

    client = SpotifyClient()
    fetcher = TrackFetcher(client.sp)
    display = DisplayManager()
    previous_track = None

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
