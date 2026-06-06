class TrackInfo:
    def __init__(self, track_id, name, artist, album, album_art_url, artist_art_url, is_playing, progress_ms, duration_ms):
        self.track_id = track_id
        self.name = name
        self.artist = artist
        self.album = album
        self.album_art_url = album_art_url
        self.artist_art_url = artist_art_url
        self.is_playing = is_playing
        self.progress_ms = progress_ms
        self.duration_ms = duration_ms

    def __eq__(self, other):
        if not isinstance(other, TrackInfo):
            return False
        return self.track_id == other.track_id and self.is_playing == other.is_playing

    def __repr__(self):
        status = "playing" if self.is_playing else "paused"
        return f"{self.name} by {self.artist} ({status})"
