import os
import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth
from track_info import TrackInfo
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI


class SpotifyClient:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope="user-read-currently-playing user-modify-playback-state"
        ))


class TrackFetcher:
    def __init__(self, sp):
        self.sp = sp
        # Path to the local JSON file on your SD card
        self.cache_file = os.path.join(
            os.path.dirname(__file__), "artist_cache.json")
        self.cache = self._load_cache()

    def _load_cache(self):
        """Reads the local JSON file from the SD card."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}  # Return empty dictionary if file is corrupted
        return {}

    def _save_cache(self):
        """Writes the updated artist list back to the local JSON file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=4)
        except Exception as e:
            print(f"Failed to save cache file: {e}")

    def get_current_track(self):
        try:
            data = self.sp.current_user_playing_track()
            if not data or not data.get('item'):
                return None

            item = data['item']

            # 1. Safely extract primary artist data
            artists = item.get('artists', [])  # might be multiple artists
            artist_id = artists[0].get('id') if artists else None
            artist_name = artists[0].get(
                'name') if artists else "Unknown Artist"

            # 2. Local File Check: Check if ID is in our local dictionary
            artist_art = None
            if artist_id:
                if artist_id in self.cache:
                    # Found locally! No network call needed.
                    artist_art = self.cache[artist_id]
                else:
                    # Not found locally. Fetch from Spotify API.
                    artist_data = self.sp.artist(artist_id)
                    if artist_data and artist_data.get('images'):
                        artist_art = artist_data['images'][0]['url']

                    # Update memory and save to the local file
                    self.cache[artist_id] = artist_art
                    self._save_cache()

            # 3. Safely handle album imagery arrays
            album = item.get('album', {})
            album_images = album.get('images', [])
            album_art_url = album_images[0]['url'] if album_images else None

            return TrackInfo(
                track_id=item.get('id'),
                name=item.get('name'),
                artist=artist_name,
                album=album.get('name'),
                album_art_url=album_art_url,
                artist_art_url=artist_art,
                is_playing=data.get('is_playing', False),
                progress_ms=data.get('progress_ms', 0),
                duration_ms=item.get('duration_ms', 0)
            )

        except Exception as e:
            print(f"Error fetching current track: {e}")
            return None

    def skip(self):
        try:
            self.sp.next_track()
        except Exception as e:
            print(f"Error skipping: {e}")

    def previous(self):
        try:
            self.sp.previous_track()
        except Exception as e:
            print(f"Error going to previous: {e}")

    def toggle_playback(self, is_playing):
        try:
            if is_playing:
                self.sp.pause_playback()
            else:
                self.sp.start_playback()
        except Exception as e:
            print(f"Error toggling playback: {e}")

    def set_volume(self, volume):
        try:
            volume = max(0, min(100, volume))
            self.sp.volume(volume)
        except Exception as e:
            print(f"Error setting volume: {e}")
