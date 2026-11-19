from ursina import *

app = Ursina()

# --- गेम की अवस्था और गहरी डिटेल ---
game_data = {
    "level": 1,
    "credits": 777,
    "ecrystals": 77,
    "unlocked_plots": 1,
    "crops": ["Wheat", "Carrot", "Corn", "Potato", "Tomato", "Strawberry", "Gold Crop"],
    "machines": ["Flour Mill", "Juice Press", "Popcorn Popper", "Chips Fryer", "Ketchup Kettle", "Jam Pot", "Gold Refiner"],
    "machine_sub_upgrades": [[1,1,1,1,1,1,1] for _ in range(7)],
    "plot_sub_blocks": [[False]*7 for _ in range(7)] 
}

window.title = "Farm 7: Agri-Estate 3D - Mobile Edition"
window.borderless = False
window.color = color.rgb(40, 100, 40)

# --- 3D कैमरा और लाइटिंग ---
camera.position = (0, 22, -25)
camera.rotation = (45, 0, 0)

sky = Entity(model='sphere', scale=150, color=color.rgb(90, 160, 90), double_sided=True)

# --- यूआई (UI) और स्टेटस बार ---
credits_text = Text(text=f"CREDITS: {game_data['credits']}", position=(-0.85, 0.45), scale=1.0, color=color.gold)
crystals_text = Text(text=f"E-CRYSTALS: {game_data['ecrystals']}", position=(-0.45, 0.45), scale=1.0, color=color.cyan)
level_text = Text(text=f"SECTOR: {game_data['level']}/7", position=(0.35, 0.45), scale=1.0, color=color.lime)

castle_label = Text(text="Rajput Agri-Palace\nTier: 1/7 (Tap Castle to Upgrade)", position=(-0.85, 0.38), scale=0.8, background=True)

# --- केंद्रीय 3D महल (मोबाइल टच से अपग्रेड होगा) ---
def upgrade_castle():
    if game_data["level"] < 7:
        game_data["level"] += 1
        level_text.text = f"SECTOR: {game_data['level']}/7"
        castle_label.text = f"Rajput Agri-Palace\nTier: {game_data['level']}/7 (Expanded)"
        print(f"Upgraded to Level {game_data['level']}")

central_castle = Entity(
    model='cube',
    color=color.rgb(210, 180, 140),
    scale=(4.5, 3.5, 4.5),
    position=(0, 1.75, 0),
    on_click=upgrade_castle  # मोबाइल पर महल छूने से अपग्रेड होगा
)
castle_roof = Entity(
    model='pyramid',
    color=color.rgb(180, 50, 50),
    scale=(5, 1.5, 5),
    position=(0, 4.25, 0)
)

# --- हार्वेस्ट बटन (मोबाइल स्क्रीन के लिए ऑन-स्क्रीन टच बटन) ---
def harvest_credits():
    game_data["credits"] += 7777
    credits_text.text = f"CREDITS: {game_data['credits']}"
    print("Harvested 7777 Credits via Mobile Touch!")

harvest_btn = Button(text='HARVEST\n(+7777)', color=color.rgb(200, 150, 0), scale=(0.25, 0.1), position=(0.7, -0.4))
harvest_btn.on_click = harvest_credits

# --- 7 मुख्य ज़मीन के प्लॉट ---
plots = []
plot_positions = [
    (-6, 0, -6), (0, 0, -6), (6, 0, -6),
    (-6, 0, 0),              (6, 0, 0),
    (-6, 0, 6),  (0, 0, 6),  (6, 0, 6)
]

for i in range(7):
    pos = plot_positions[i]
    is_unlocked = (i < game_data["unlocked_plots"])
    
    plot = Entity(
        model='cube',
        color=color.rgb(110, 80, 50) if is_unlocked else color.rgb(50, 50, 50),
        scale=(4, 0.2, 4),
        position=pos
    )
    
    if not is_unlocked:
        Text(text=f"LOCKED\n[Plot 7.{i+1}]", parent=plot, position=(-0.35, 2, 0), scale=4.5, color=color.yellow)
    else:
        Text(text=f"Crop: {game_data['crops'][i]}", parent=plot, position=(-0.4, 2, 0), scale=3.5, color=color.white)
        for sb in range(7):
            sub_x = -1.2 + (sb % 3) * 1.2
            sub_z = -1.2 + (sb // 3) * 1.2
            Entity(parent=plot, model='cube', color=color.rgb(80, 140, 60), scale=(0.9, 0.4, 0.9), position=(sub_x, 0.5, sub_z))

    plots.append(plot)

# --- 7 प्रोसेसिंग मशीनें ---
machines = []
machine_positions = [
    (-9, 0, -4), (-9, 0, 0), (-9, 0, 4),
    (9, 0, -4),  (9, 0, 0),  (9, 0, 4), (0, 0, -9)
]

for j in range(7):
    m_pos = machine_positions[j]
    machine = Entity(
        model='cube',
        color=color.rgb(90, 90, 110),
        scale=(2, 1.8, 2),
        position=m_pos
    )
    sub_lvl_sum = sum(game_data["machine_sub_upgrades"][j])
    Text(text=f"{game_data['machines'][j]}\nParts: {sub_lvl_sum}/49", parent=machine, position=(-0.45, 1.3, 0), scale=3, color=color.cyan)
    machines.append(machine)

def update():
    pass

app.run()

