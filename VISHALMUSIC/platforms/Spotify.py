# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Spotify Track, Album & Playlist Handler
# ═══════════════════════════════════════════════════════════

import re
import asyncio

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from py_yt import VideosSearch

import config


class SpotifyAPI:
    def __init__(self):
        self.regex = r"^https:\/\/open\.spotify\.com\/.+"
        self.client_id = config.SPOTIFY_CLIENT_ID
        self.client_secret = config.SPOTIFY_CLIENT_SECRET
        if self.client_id and self.client_secret:
            self.client_credentials_manager = SpotifyClientCredentials(
                self.client_id, self.client_secret
            )
            self.spotify = spotipy.Spotify(
                client_credentials_manager=self.client_credentials_manager
            )
        else:
            self.spotify = None

    async def valid(self, link: str) -> bool:
        return bool(re.search(self.regex, link or ""))

    async def track(self, link: str):
        if not self.spotify:
            raise RuntimeError("Spotify credentials not configured")
        track = await asyncio.to_thread(self.spotify.track, link)
        info = track.get("name", "")
        for artist in track.get("artists", []):
            fetched = f' {artist.get("name", "")}'
            if "Various Artists" not in fetched:
                info += fetched
        results = VideosSearch(info, limit=1)
        data = await results.next()
        result_list = data.get("result", [])
        if not result_list or len(result_list) == 0:
            raise RuntimeError("No YouTube results found for Spotify track")
        r = result_list[0]
        track_details = {
            "title": r.get("title", ""),
            "link": r.get("link", ""),
            "vidid": r.get("id", ""),
            "duration_min": r.get("duration", ""),
            "thumb": r.get("thumbnails", [{}])[0].get("url", "").split("?")[0],
        }
        return track_details, track_details["vidid"]

    async def playlist(self, url):
        if not self.spotify:
            raise RuntimeError("Spotify credentials not configured")
        playlist = await asyncio.to_thread(self.spotify.playlist, url)
        playlist_id = playlist.get("id", "")
        results = []
        for item in playlist.get("tracks", {}).get("items", []):
            music_track = item.get("track", {})
            info = music_track.get("name", "")
            for artist in music_track.get("artists", []):
                fetched = f' {artist.get("name", "")}'
                if "Various Artists" not in fetched:
                    info += fetched
            results.append(info)
        return results, playlist_id

    async def album(self, url):
        if not self.spotify:
            raise RuntimeError("Spotify credentials not configured")
        album = await asyncio.to_thread(self.spotify.album, url)
        album_id = album.get("id", "")
        results = []
        for item in album.get("tracks", {}).get("items", []):
            info = item.get("name", "")
            for artist in item.get("artists", []):
                fetched = f' {artist.get("name", "")}'
                if "Various Artists" not in fetched:
                    info += fetched
            results.append(info)
        return results, album_id

    async def artist(self, url):
        if not self.spotify:
            raise RuntimeError("Spotify credentials not configured")
        artistinfo = await asyncio.to_thread(self.spotify.artist, url)
        artist_id = artistinfo.get("id", "")
        results = []
        artisttoptracks = await asyncio.to_thread(self.spotify.artist_top_tracks, url)
        for item in artisttoptracks.get("tracks", []):
            info = item.get("name", "")
            for artist in item.get("artists", []):
                fetched = f' {artist.get("name", "")}'
                if "Various Artists" not in fetched:
                    info += fetched
            results.append(info)
        return results, artist_id

# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
