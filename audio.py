import os

from kivy.core.audio import SoundLoader

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

# Vibration milliseconds mein. Sirf jo events important hain, unhe hi vibrate karenge.
VIBE_MS = {"harvest": 40, "unlock": 60, "upgrade": 25, "boost": 80, "tier": 150, "error": 30}


def _load(rel):
    path = os.path.join(BASE, rel)
    if not os.path.exists(path):
        return None
    return SoundLoader.load(path)


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
            self.music.loop = True
            self.music.volume = 0.35

    def play(self, key):
        if not self.settings["sfx"]:
            return
        s = self.sounds.get(key)
        if s:
            s.stop()
            s.play()

    def vibrate_for(self, key):
        if not self.settings["vibe"]:
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
        if self.music and self.settings["music"] and not self._music_playing:
            self.music.play()
            self._music_playing = True

    def apply_music_setting(self):
        if not self.music:
            return
        if self.settings["music"]:
            self.start_music()
        else:
            self.music.stop()
            self._music_playing = False

    def pause(self):
        if self.music:
            self.music.stop()
            self._music_playing = False

    def resume(self):
        self.start_music()
