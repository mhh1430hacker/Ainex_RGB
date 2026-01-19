import cv2
import numpy as np
import time
import json
import os
import random
import sys

# === Immortality Settings ===
MEMORY_FILE = "ainex_memory.json"
VIDEO_DIR = "ainex_evidence"
RUN_LIMIT_SEC = 5.8 * 3600  # 5 hours and 48 minutes (to stop the script before it is kicked out)
VIDEO_INTERVAL = 3 * 3600   # Video every 3 hours
START_TIME = time.time()

# === Make sure the videos folder exists ===
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

# === Warrior Classes (for simulation) ===
class Fighter:
    def __init__(self, name, is_fluid):
        self.name = name
        self.is_fluid = is_fluid # True = Ainex, False = Old AI
        self.level = 1
        self.xp = 0
        self.hp = 100
        
    def to_dict(self):
        return {"name": self.name, "lvl": self.level, "xp": self.xp, "hp": self.hp}
    
    def from_dict(self, data):
        self.level = data['lvl']
        self.xp = data['xp']
        self.hp = data['hp']

# === Status System (Memory) ===
def load_state():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            data = json.load(f)
        
        ainex = Fighter("AINEX", True)
        legacy = Fighter("LEGACY_AI", False)
        ainex.from_dict(data['ainex'])
        legacy.from_dict(data['legacy'])
        
        return ainex, legacy, data['last_video_time'], data['total_cycles']
    else:
        return Fighter("AINEX", True), Fighter("LEGACY_AI", False), 0, 0

def save_state(ainex, legacy, last_vid, cycles):
    data = {
        "ainex": ainex.to_dict(),
        "legacy": legacy.to_dict(),
        "last_video_time": last_vid,
        "total_cycles": cycles,
        "updated_at": time.ctime()
    }
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# This is the video render engine.
def render_battle_video(ainex, legacy, cycle_count):
    filename = f"{VIDEO_DIR}/battle_log_{int(time.time())}.mp4"
    width, height = 1280, 720
    fps = 24
    seconds = 30 # Video length Summary
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    print(f">>> RENDERING EVIDENCE VIDEO: {filename}...")
    
    for i in range(fps * seconds):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Technical background
        cv2.rectangle(frame, (0, 0), (width, height), (10, 10, 10), -1)
        
        # Battle Visuals Simulation
        # Aynx (Gold) Grows
        ainex_radius = 50 + (i % 50) + (ainex.level * 2)
        cv2.circle(frame, (300, 360), int(ainex_radius), (0, 215, 255), 2)
        cv2.putText(frame, "AINEX CORE", (220, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 215, 255), 2)
        
        # The old AI (red) is shaking.
        jitter = random.randint(-5, 5)
        legacy_radius = max(10, 50 - (i % 20) + (legacy.level))
        cv2.circle(frame, (900 + jitter, 360 + jitter), int(legacy_radius), (0, 0, 255), 2)
        cv2.putText(frame, "LEGACY MODEL", (820, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Texts
        cv2.putText(frame, f"SYSTEM TIME: {time.ctime()}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, f"TOTAL CYCLES: {cycle_count}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        # Status bar
        cv2.rectangle(frame, (50, 600), (50 + ainex.level*10, 630), (0, 215, 255), -1)
        cv2.putText(frame, f"AINEX LEVEL: {ainex.level}", (50, 650), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        
        out.write(frame)
        
    out.release()
    print(">>> VIDEO RENDER COMPLETE.")

# === Main ring (The Infinite Loop) ===
def main():
    print(">>> AINEX INFINITE PROTOCOL INITIATED.")
    ainex, legacy, last_video_time, total_cycles = load_state()
    
    # Workshop (continues until closing time)
    while True:
        current_time = time.time()
        
        #1. Safety check (Are we close to 6 hours?)
        if current_time - START_TIME > RUN_LIMIT_SEC:
            print(">>> RUNTIME LIMIT REACHED. PREPARING FOR REINCARNATION...")
            save_state(ainex, legacy, last_video_time, total_cycles)
            break
            
        #2. Simulation (ongoing battle)
        total_cycles += 1
        
        # Ainex continuously gains experience (liquid learning)
        ainex.xp += random.randint(1, 5)
        if ainex.xp > 100 * ainex.level:
            ainex.level += 1
            ainex.xp = 0
            
        # Old AI stumbles (stagnation)
        if random.random() < 0.3:
            legacy.xp += 1 # Learns slowly
        else:
            legacy.hp -= 0.1 # Eroded
            
        # 3. Check the video (has it been 3 hours?)
        # We use current_time instead of START_TIME because we calculate real time across days.
        if current_time - last_video_time > VIDEO_INTERVAL:
            print(">>> 3 HOURS PASSED. GENERATING PROOF...")
            render_battle_video(ainex, legacy, total_cycles)
            last_video_time = current_time # Time Update
            save_state(ainex, legacy, last_video_time, total_cycles) # Immediate saving
            
        # Save every 10 minutes for safety
        if total_cycles % 600 == 0:
            save_state(ainex, legacy, last_video_time, total_cycles)
            
        # Simulation speed
        time.sleep(1)

if __name__ == "__main__":
    main()
