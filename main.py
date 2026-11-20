import json
import math
import os
import traceback

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

try:
    from audio import Audio
except Exception:
    traceback.print_exc()
    Audio = None

N = 7
HARVEST_UNITS = 7
CRYSTALS_PER_GOLD = 7
BOOST_COST = 7
SAVE_NAME = "save.json"
MAX_DT = 1.0  # ek tick mein zyada se zyada 1 second ka time

# (naam, daam per unit, ugne ka time sec)
CROPS = [
    ("Wheat", 10, 5), ("Carrot", 15, 8), ("Corn", 25, 12), ("Potato", 35, 16),
    ("Tomato", 50, 20), ("Strawberry", 70, 25), ("Gold Crop", 150, 40),
]

# (naam, base income per second)
MACHINES = [
    ("Flour Mill", 0.5), ("Juice Press", 0.8), ("Popcorn Popper", 1.0),
    ("Chips Fryer", 1.5), ("Ketchup Kettle", 2.0), ("Jam Pot", 3.0),
    ("Gold Refiner", 5.0),
]

CHAPTERS = [
    "Chapter 1: Ek chhota khet. Veer Singh ne pehla beej bo diya.",
    "Chapter 2: Gaon ki chakki chalu hui. Ab aata bikne laga.",
    "Chapter 3: Makka ki fasal aayi, mele mein naam hua.",
    "Chapter 4: Aloo aur chips ki factory ne gaon roshan kiya.",
    "Chapter 5: Tamatar ki ketchup se shahar tak raasta bana.",
    "Chapter 6: Strawberry jam ki khushboo se raja ka darbar mehka.",
    "Chapter 7: Sone ki fasal! Agri-Palace poora bana, kahani amar hui.",
]

STORY_INTRO = (
    "Bahut pehle ki baat hai. Veer Singh ko apne dada ji se sirf ek chhota khet mila.\n\n"
    "Unhone kasam khayi ki wo 7 sector wala Rajput Agri-Palace banayenge.\n\n"
    "Har sector ek nayi fasal, ek nayi machine aur ek naya raaz laata hai.\n\n"
    "Kya aap Veer Singh ki madad karenge?"
)

GUIDE = (
    "7 KA KHEL\n"
    "7 khet, 7 fasal, 7 machine, har machine mein 7 part, 7 castle tier, aur har katai mein 7 unit.\n\n"
    "KAISE KHELEIN\n"
    "1. Khet par tap karke beej bo'o. Fasal ugne mein time leti hai.\n"
    "2. Fasal TAYAR hone par tap karke kaato, paisa milega.\n"
    "3. Machines apne aap paisa dete hain (per second).\n"
    "4. Machine par tap karke uska sabse kamzor part upgrade karo. Income badhegi.\n"
    "5. Castle tier upgrade karo. Har tier par sab kamai par bonus milta hai aur naya chapter khulta hai.\n"
    "6. Gold Crop kaatne par crystals milte hain. BOOST se sab ugi fasalen turant tayar ho jati hain.\n\n"
    "CHETAVNI\n"
    "Pehle sasta kaam karo, phir mehenga. Khet unlock karna kabhi mat bhoolna."
)

COL_LOCKED = (0.3, 0.3, 0.3, 1)
COL_EMPTY = (0.55, 0.4, 0.25, 1)
COL_GROW = (0.35, 0.65, 0.35, 1)
COL_READY = (0.9, 0.7, 0.1, 1)
COL_MACHINE = (0.35, 0.35, 0.5, 1)
COL_CASTLE = (0.75, 0.6, 0.45, 1)
COL_BOOST = (0.3, 0.6, 0.9, 1)
COL_SETTING = (0.4, 0.4, 0.55, 1)


def new_state():
    return {
        "credits": 777.0,
        "crystals": 77,
        "tier": 1,
        "plots": [{"unlocked": i == 0, "state": "empty", "timer": 0.0} for i in range(N)],
        "parts": [[1] * N for _ in range(N)],
        "settings": {"sfx": True, "music": True, "vibe": True},
    }


state = new_state()


class NoAudio:
    """Audio na chale to game isi se chalta hai."""
    def __init__(self, settings):
        self.settings = settings

    def play(self, key):
        pass

    def vibrate_for(self, key):
        pass

    def start_music(self):
        pass

    def apply_music_setting(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass


def guarded(fn):
    """Handler mein error aaye to app band na ho, sirf log mein print ho."""
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            traceback.print_exc()
    return wrapper


# ---------- Game logic: har function (message, sound_key) return karta hai ----------

def tier_now():
    return min(N, max(1, int(state["tier"])))


def bonus():
    return 1 + 0.1 * (tier_now() - 1)


def plot_cost(i):
    return 300 * i


def castle_cost():
    return 500 * tier_now()


def machine_income(j):
    return MACHINES[j][1] * sum(state["parts"][j]) / N * bonus()


def total_income():
    return sum(machine_income(j) for j in range(N))


def plant_or_harvest(i):
    p = state["plots"][i]
    name, price, secs = CROPS[i]

    if not p["unlocked"]:
        if i == 0 or not state["plots"][i - 1]["unlocked"]:
            return "Pehle pichla khet unlock karo", "error"
        cost = plot_cost(i)
        if state["credits"] < cost:
            return f"Ye khet unlock karne ke liye {cost} credits chahiye", "error"
        state["credits"] -= cost
        p["unlocked"] = True
        return f"{name} ka khet unlock ho gaya!", "unlock"

    if p["state"] == "empty":
        p["state"] = "growing"
        p["timer"] = float(secs)
        return f"{name} ka beej bo diya", "plant"

    if p["state"] == "growing":
        return f"{name} abhi ug raha hai, {math.ceil(p['timer'])} second baaki", "error"

    gain = price * HARVEST_UNITS * bonus()
    state["credits"] += gain
    msg = f"{name} kaata! +{int(gain)} credits"
    if i == N - 1:
        state["crystals"] += CRYSTALS_PER_GOLD
        msg += f", +{CRYSTALS_PER_GOLD} crystals"
    p["state"] = "empty"
    p["timer"] = 0.0
    return msg, "harvest"


def upgrade_machine(j):
    parts = state["parts"][j]
    name = MACHINES[j][0]
    if min(parts) >= N:
        return f"{name} poori tarah upgrade ho chuki hai", "error"
    k = parts.index(min(parts))
    cost = 50 * parts[k]
    if state["credits"] < cost:
        return f"{name} upgrade ke liye {cost} credits chahiye", "error"
    state["credits"] -= cost
    parts[k] += 1
    return f"{name} ka part {k + 1} level {parts[k]} par pahuncha", "upgrade"


def upgrade_castle():
    t = tier_now()
    if t >= N:
        return "Castle sabse upar wale tier par hai", "error"
    cost = castle_cost()
    if state["credits"] < cost:
        return f"Tier {t + 1} ke liye {cost} credits chahiye", "error"
    state["credits"] -= cost
    state["tier"] = t + 1
    return f"Tier {t + 1} unlock! {CHAPTERS[t]}", "tier"


def boost():
    if state["crystals"] < BOOST_COST:
        return f"BOOST ke liye {BOOST_COST} crystals chahiye", "error"
    growing = [p for p in state["plots"] if p["state"] == "growing"]
    if not growing:
        return "Abhi koi fasal ug nahi rahi", "error"
    state["crystals"] -= BOOST_COST
    for p in growing:
        p["timer"] = 0.0
        p["state"] = "ready"
    return "BOOST! Sab fasalen tayar ho gayi", "boost"


def game_tick(dt):
    dt = min(max(dt, 0.0), MAX_DT)
    for p in state["plots"]:
        if p["state"] == "growing":
            p["timer"] -= dt
            if p["timer"] <= 0:
                p["timer"] = 0.0
                p["state"] = "ready"
    state["credits"] += total_income() * dt


# ---------- Save / Load ----------

def save_game(path):
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f)
        os.replace(tmp, path)
    except Exception:
        traceback.print_exc()


def load_game(path):
    """Save file validate karke load karta hai. Kuch galat ho to default rakhta hai."""
    if not os.path.exists(path):
        return
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return

        fresh = new_state()
        fresh["credits"] = max(0.0, float(data.get("credits", fresh["credits"])))
        fresh["crystals"] = max(0, int(data.get("crystals", fresh["crystals"])))
        fresh["tier"] = min(N, max(1, int(data.get("tier", 1))))

        plots = data.get("plots", [])
        for i in range(N):
            if i < len(plots) and isinstance(plots[i], dict):
                p = plots[i]
                st = p.get("state", "empty")
                if st not in ("empty", "growing", "ready"):
                    st = "empty"
                fresh["plots"][i] = {
                    "unlocked": bool(p.get("unlocked", i == 0)) or i == 0,
                    "state": st,
                    "timer": max(0.0, float(p.get("timer", 0.0))),
                }

        parts = data.get("parts", [])
        for j in range(N):
            if j < len(parts) and isinstance(parts[j], list) and len(parts[j]) == N:
                fresh["parts"][j] = [min(N, max(1, int(x))) for x in parts[j]]

        s = data.get("settings", {})
        if isinstance(s, dict):
            for k in fresh["settings"]:
                fresh["settings"][k] = bool(s.get(k, fresh["settings"][k]))

        state.clear()
        state.update(fresh)
    except Exception:
        traceback.print_exc()


# ---------- UI helpers ----------

def wrap(label, auto_height=True):
    label.bind(width=lambda w, v: setattr(w, "text_size", (v, None)))
    if auto_height:
        label.size_hint_y = None
        label.bind(texture_size=lambda w, ts: setattr(w, "height", ts[1]))


class StoryScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        box = BoxLayout(orientation="vertical", padding=20, spacing=15)
        title = Label(text="[b]FARM 7: AGRI-ESTATE[/b]", markup=True,
                      font_size="26sp", size_hint_y=None, height=70)
        story = Label(text=STORY_INTRO, halign="center", valign="middle", font_size="17sp")
        wrap(story, auto_height=False)
        start = Button(text="Khel Shuru Karo", size_hint_y=None, height=70,
                       background_color=COL_GROW)
        start.bind(on_release=self.start)
        box.add_widget(title)
        box.add_widget(story)
        box.add_widget(start)
        self.add_widget(box)

    @guarded
    def start(self, *args):
        app = App.get_running_app()
        app.audio.start_music()
        app.audio.play("tap")
        app.root.current = "game"


class GameScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=8, spacing=6)

        self.top_lbl = Label(size_hint_y=None, height=60, font_size="15sp", halign="center")
        wrap(self.top_lbl, auto_height=False)
        self.msg = Label(size_hint_y=None, height=40, font_size="14sp",
                         color=(1, 0.85, 0.4, 1), halign="center")
        wrap(self.msg, auto_height=False)
        root.add_widget(self.top_lbl)
        root.add_widget(self.msg)

        tabs = TabbedPanel(do_default_tab=False, tab_width=110)

        # --- Khet tab ---
        farm = BoxLayout(orientation="vertical", spacing=6, padding=4)
        self.boost_btn = Button(size_hint_y=None, height=55, background_color=COL_BOOST)
        self.boost_btn.bind(on_release=lambda *_: self.act(boost))
        farm.add_widget(self.boost_btn)
        grid = GridLayout(cols=1, size_hint_y=None, spacing=6)
        grid.bind(minimum_height=grid.setter("height"))
        self.plot_btns = []
        for i in range(N):
            b = Button(size_hint_y=None, height=75)
            b.bind(on_release=lambda _b, idx=i: self.act(plant_or_harvest, idx))
            grid.add_widget(b)
            self.plot_btns.append(b)
        sv = ScrollView()
        sv.add_widget(grid)
        farm.add_widget(sv)
        self.add_tab(tabs, "Khet", farm)

        # --- Factory tab ---
        factory = BoxLayout(orientation="vertical", spacing=6, padding=4)
        hint = Label(text="Machines apne aap paisa dete hain. Upgrade se income badhegi.",
                     size_hint_y=None, height=40, font_size="13sp")
        wrap(hint, auto_height=False)
        factory.add_widget(hint)
        grid2 = GridLayout(cols=1, size_hint_y=None, spacing=6)
        grid2.bind(minimum_height=grid2.setter("height"))
        self.machine_btns = []
        for j in range(N):
            b = Button(size_hint_y=None, height=85, background_color=COL_MACHINE)
            b.bind(on_release=lambda _b, idx=j: self.act(upgrade_machine, idx))
            grid2.add_widget(b)
            self.machine_btns.append(b)
        sv2 = ScrollView()
        sv2.add_widget(grid2)
        factory.add_widget(sv2)
        self.add_tab(tabs, "Factory", factory)

        # --- Castle tab ---
        castle = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.castle_info = Label(halign="center", valign="middle", font_size="16sp")
        wrap(self.castle_info)
        self.castle_btn = Button(size_hint_y=None, height=80, background_color=COL_CASTLE)
        self.castle_btn.bind(on_release=lambda *_: self.act(upgrade_castle))
        castle.add_widget(self.castle_info)
        castle.add_widget(self.castle_btn)
        self.add_tab(tabs, "Castle", castle)

        # --- Settings tab ---
        settings = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.sfx_btn = Button(size_hint_y=None, height=70, background_color=COL_SETTING)
        self.sfx_btn.bind(on_release=lambda *_: self.toggle("sfx"))
        self.music_btn = Button(size_hint_y=None, height=70, background_color=COL_SETTING)
        self.music_btn.bind(on_release=lambda *_: self.toggle("music"))
        self.vibe_btn = Button(size_hint_y=None, height=70, background_color=COL_SETTING)
        self.vibe_btn.bind(on_release=lambda *_: self.toggle("vibe"))
        settings.add_widget(self.sfx_btn)
        settings.add_widget(self.music_btn)
        settings.add_widget(self.vibe_btn)
        self.add_tab(tabs, "Settings", settings)

        # --- Guide tab ---
        guide_lbl = Label(text=GUIDE, halign="left", valign="top", font_size="15sp")
        wrap(guide_lbl)
        sv3 = ScrollView()
        sv3.add_widget(guide_lbl)
        self.add_tab(tabs, "Guide", sv3)

        root.add_widget(tabs)
        self.add_widget(root)
        self.refresh()

    def add_tab(self, tabs, title, content):
        item = TabbedPanelItem(text=title)
        item.add_widget(content)
        tabs.add_widget(item)

    @guarded
    def act(self, fn, *args):
        msg, sfx = fn(*args)
        self.msg.text = msg
        app = App.get_running_app()
        app.audio.play(sfx)
        app.audio.vibrate_for(sfx)
        self.refresh()

    @guarded
    def toggle(self, key):
        app = App.get_running_app()
        s = state["settings"]
        s[key] = not s[key]
        if key == "music":
            app.audio.apply_music_setting()
        app.audio.play("tap")
        self.refresh()

    @guarded
    def on_tick(self, dt):
        game_tick(dt)
        self.refresh()

    @guarded
    def refresh(self):
        inc = total_income()
        self.top_lbl.text = (f"Credits: {int(state['credits'])}   Crystals: {state['crystals']}\n"
                             f"Income: {inc:.1f}/sec   Castle Tier: {tier_now()}/{N}")

        for i, b in enumerate(self.plot_btns):
            name, price, _secs = CROPS[i]
            p = state["plots"][i]
            if not p["unlocked"]:
                b.text = f"LOCKED Khet {i + 1}\nUnlock: {plot_cost(i)} credits"
                b.background_color = COL_LOCKED
            elif p["state"] == "empty":
                b.text = f"{name}: khet khaali\nTap karke beej bo'o"
                b.background_color = COL_EMPTY
            elif p["state"] == "growing":
                b.text = f"{name}: ug raha hai\n{math.ceil(p['timer'])} sec baaki"
                b.background_color = COL_GROW
            else:
                b.text = f"{name}: TAYAR!\nTap karke kaato (+{int(price * HARVEST_UNITS * bonus())})"
                b.background_color = COL_READY

        self.boost_btn.text = f"BOOST: sab fasalen turant tayar ({BOOST_COST} crystals)"

        for j, b in enumerate(self.machine_btns):
            name = MACHINES[j][0]
            parts = state["parts"][j]
            upg = "MAX" if min(parts) >= N else f"{50 * min(parts)} credits"
            b.text = (f"{name}\nParts {sum(parts)}/{N * N}  |  +{machine_income(j):.1f}/sec\n"
                      f"Upgrade: {upg}")

        t = tier_now()
        self.castle_info.text = (f"Rajput Agri-Palace - Tier {t}/{N}\n\n"
                                 f"{CHAPTERS[t - 1]}")
        if t < N:
            self.castle_btn.text = f"Tier {t + 1} upgrade: {castle_cost()} credits"
        else:
            self.castle_btn.text = "Castle MAX ho gaya!"

        s = state["settings"]
        self.sfx_btn.text = f"Sound effects: {'ON' if s['sfx'] else 'OFF'}"
        self.music_btn.text = f"Background music: {'ON' if s['music'] else 'OFF'}"
        self.vibe_btn.text = f"Vibration: {'ON' if s['vibe'] else 'OFF'}"


class FarmApp(App):
    def build(self):
        self.title = "Farm 7: Agri-Estate"
        try:
            self.save_path = os.path.join(self.user_data_dir, SAVE_NAME)
            load_game(self.save_path)

            try:
                self.audio = Audio(state["settings"]) if Audio else NoAudio(state["settings"])
            except Exception:
                traceback.print_exc()
                self.audio = NoAudio(state["settings"])

            sm = ScreenManager()
            sm.add_widget(StoryScreen(name="story"))
            sm.add_widget(GameScreen(name="game"))

            Clock.schedule_interval(lambda dt: save_game(self.save_path), 10)
            return sm
        except Exception:
            err = traceback.format_exc()
            traceback.print_exc()
            box = ScrollView()
            lbl = Label(text="Game shuru nahi ho paya. Ye error screenshot lekar bhejein:\n\n" + err,
                        font_size="12sp", halign="left", valign="top")
            wrap(lbl)
            box.add_widget(lbl)
            return box

    def on_pause(self):
        save_game(self.save_path)
        try:
            self.audio.pause()
        except Exception:
            traceback.print_exc()
        return True

    def on_resume(self):
        try:
            self.audio.resume()
        except Exception:
            traceback.print_exc()

    def on_stop(self):
        save_game(self.save_path)


if __name__ == "__main__":
    FarmApp().run()
