import cv2
import numpy as np
import time
import json
import os
import random
import sys

# === إعدادات الخلود ===
MEMORY_FILE = "ainex_memory.json"
VIDEO_DIR = "ainex_evidence"
RUN_LIMIT_SEC = 5.8 * 3600  # 5 ساعات و 48 دقيقة (لإيقاف السكربت قبل طرده)
VIDEO_INTERVAL = 3 * 3600   # فيديو كل 3 ساعات
START_TIME = time.time()

# === التأكد من وجود مجلد الفيديوهات ===
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

# === فئات المحاربين (للمحاكاة) ===
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

# === نظام الحالة (الذاكرة) ===
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

# === مولد الفيديو (Render Engine) ===
def render_battle_video(ainex, legacy, cycle_count):
    filename = f"{VIDEO_DIR}/battle_log_{int(time.time())}.mp4"
    width, height = 1280, 720
    fps = 24
    seconds = 30 # مدة الفيديو ملخص
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    print(f">>> RENDERING EVIDENCE VIDEO: {filename}...")
    
    for i in range(fps * seconds):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # خلفية تقنية
        cv2.rectangle(frame, (0, 0), (width, height), (10, 10, 10), -1)
        
        # محاكاة بصريات المعركة
        # آينكس (ذهبي) ينمو
        ainex_radius = 50 + (i % 50) + (ainex.level * 2)
        cv2.circle(frame, (300, 360), int(ainex_radius), (0, 215, 255), 2)
        cv2.putText(frame, "AINEX CORE", (220, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 215, 255), 2)
        
        # الـ AI القديم (أحمر) يرتجف
        jitter = random.randint(-5, 5)
        legacy_radius = max(10, 50 - (i % 20) + (legacy.level))
        cv2.circle(frame, (900 + jitter, 360 + jitter), int(legacy_radius), (0, 0, 255), 2)
        cv2.putText(frame, "LEGACY MODEL", (820, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # النصوص
        cv2.putText(frame, f"SYSTEM TIME: {time.ctime()}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, f"TOTAL CYCLES: {cycle_count}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        # شريط الحالة
        cv2.rectangle(frame, (50, 600), (50 + ainex.level*10, 630), (0, 215, 255), -1)
        cv2.putText(frame, f"AINEX LEVEL: {ainex.level}", (50, 650), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        
        out.write(frame)
        
    out.release()
    print(">>> VIDEO RENDER COMPLETE.")

# === الحلقة الرئيسية (The Infinite Loop) ===
def main():
    print(">>> AINEX INFINITE PROTOCOL INITIATED.")
    ainex, legacy, last_video_time, total_cycles = load_state()
    
    # حلقة العمل (تستمر حتى يقترب وقت الإغلاق)
    while True:
        current_time = time.time()
        
        # 1. فحص الأمان (هل اقتربنا من الـ 6 ساعات؟)
        if current_time - START_TIME > RUN_LIMIT_SEC:
            print(">>> RUNTIME LIMIT REACHED. PREPARING FOR REINCARNATION...")
            save_state(ainex, legacy, last_video_time, total_cycles)
            break
            
        # 2. المحاكاة (المعركة المستمرة)
        total_cycles += 1
        
        # آينكس يكتسب خبرة باستمرار (التعلم السائل)
        ainex.xp += random.randint(1, 5)
        if ainex.xp > 100 * ainex.level:
            ainex.level += 1
            ainex.xp = 0
            
        # الـ AI القديم يتعثر (الجمود)
        if random.random() < 0.3:
            legacy.xp += 1 # يتعلم ببطء
        else:
            legacy.hp -= 0.1 # يتآكل
            
        # 3. فحص الفيديو (هل مرت 3 ساعات؟)
        # نستخدم current_time وليس START_TIME لأننا نحسب الوقت الحقيقي عبر الأيام
        if current_time - last_video_time > VIDEO_INTERVAL:
            print(">>> 3 HOURS PASSED. GENERATING PROOF...")
            render_battle_video(ainex, legacy, total_cycles)
            last_video_time = current_time # تحديث الوقت
            save_state(ainex, legacy, last_video_time, total_cycles) # حفظ فوري

        # حفظ دوري كل 10 دقائق للأمان
        if total_cycles % 600 == 0:
            save_state(ainex, legacy, last_video_time, total_cycles)
            
        # سرعة المحاكاة
        time.sleep(1)

if __name__ == "__main__":
    main()
