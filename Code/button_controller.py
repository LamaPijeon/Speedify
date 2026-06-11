from gpiozero import Button
from spotify_client import TrackFetcher


class ButtonController:
    def __init__(self, fetcher: TrackFetcher, prev_pin=17, pause_pin=27, skip_pin=22):
        self.fetcher = fetcher

        self.prev_btn = Button(prev_pin, pull_up=True)
        self.pause_btn = Button(pause_pin, pull_up=True)
        self.skip_btn = Button(skip_pin, pull_up=True)

        self.prev_btn.when_pressed = self.on_prev
        self.pause_btn.when_pressed = self.on_pause
        self.skip_btn.when_pressed = self.on_skip

    def on_prev(self):
        self.fetcher.previous()

    def on_pause(self):
        track = self.fetcher.get_current_track()
        if track:
            self.fetcher.toggle_playback(track.is_playing)

    def on_skip(self):
        self.fetcher.skip()
