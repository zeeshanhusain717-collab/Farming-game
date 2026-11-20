import os
import traceback

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

SFX_FILES = {
    "tap": "sfx/tap.ogg",
    "plant": "sfx/plant.ogg",
    "harvest": "sfx/harvest.ogg",
    "unlock": "sfx/unlock.ogg",
    "upgrade": "sfx/upgrade.ogg",
    "boost": "sfx/boost.ogg",
    "tier": "sfx/tier.ogg",
    "error": "sfx/error.ogg",
}
MUSIC_FILE = "music/farm_theme.ogg"

# Vibration milliseconds mein
VIBE_MS = {"harvest": 40, "unlock": 60, "upgrade": 25, "boost": 80, "tier": 150, "error": 30}

try:
    from kivy.core.audio import SoundLoader
except Exception:
    traceback.print_exc()
    SoundLoader = None


def _load(rel):
    """Khaali ya missing file par None return karta hai. Crash nahi karta."""
    try:
        path = os.path.join(BASE, rel)
        if SoundLoader is None or not os.path.exists(path):
            return None
        if os.path.getsize(path) == 0:
            return None
        return SoundLoader.load(path)
    except Exception:
        traceback.print_exc()
        return None


class Audio:
    def __init__(self, settings):
        self.settings = settings
        self.sounds = {}
        self._music_playing = False

        for key, rel in SFX_FILES.items():
            s = _load(rel)
            if s:
                s.volume = 0.8
                self.sounds[key] = s

        self.music = _load(MUSIC_FILE)
        if self.music:
            try:
                self.music.loop = True
                self.music.volume = 0.35
            except Exception:
                traceback.print_exc()

    def play(self, key):
        if not self.settings.get("sfx"):
            return
        s = self.sounds.get(key)
        if not s:
            return
        try:
            s.stop()
            s.play()
        except Exception:
            traceback.print_exc()

    def vibrate_for(self, key):
        if not self.settings.get("vibe"):
            return
        ms = VIBE_MS.get(key)
        if not ms:
            return
        try:
            from plyer import vibrator
            vibrator.vibrate(ms / 1000.0)
        except Exception:
            # Desktop par ya permission na ho to chupchap skip
            pass

    def start_music(self):
        if not self.music or not self.settings.get("music") or self._music_playing:
            return
        try:
            self.music.play()
            self._music_playing = True
        except Exception:
            traceback.print_exc()

    def apply_music_setting(self):
        if self.settings.get("music"):
            self.start_music()
        else:
            self.pause()

    def pause(self):
        if not self.music:
            return
        try:
            self.music.stop()
        except Exception:
            traceback.print_exc()
        self._music_playing = False

    def resume(self):
        self.start_music()
