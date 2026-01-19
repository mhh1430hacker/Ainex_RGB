import pybullet as p
import pybullet_data
import time
import numpy as np
import cv2
import json
import os
import random

# === إعدادات الخلود ===
MEMORY_FILE = "ainex_memory.json"
VIDEO_FILENAME = "ainex_latest_evidence.mp4"
CYCLES_PER_RUN = 1000  # عدد دورات المحاكاة في كل تشغيلة (لإنتاج فيديو قصير ودسم)
WIDTH, HEIGHT = 640, 480 # دقة مناسبة للمعالج

# === تحميل الذاكرة (للاستمرار من حيث توقفنا) ===
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, 'r') as f:
        memory = json.load(f)
else:
    memory = {"ainex_lvl": 1, "legacy_lvl": 1, "total_cycles": 0, "disasters_survived": 0}

# === إعداد المحرك الفيزيائي ===
# نستخدم DIRECT للسرعة، لكن الكاميرا ستعمل عبر TinyRenderer
p.connect(p.DIRECT) 
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)

# بناء الأرضية
planeId = p.loadURDF("plane.urdf")
p.changeDynamics(planeId, -1, lateralFriction=1.0) # أرضية خشنة

# === وظائف البناء ===
def build_tower(offset_x, level, is_fluid):
    """يبني برجاً من المكعبات. آينكس يستخدم مفاصل مرنة، القديم مجرد رص"""
    blocks = []
    base_pos = [offset_x, 0, 0.5]
    
    for i in range(level + 3): # كل مستوى يزيد الارتفاع
        pos = [offset_x, 0, 0.5 + i]
        # مكعب بكتلة حقيقية
        block = p.loadURDF("cube_small.urdf", pos, globalScaling=1.5)
        p.changeDynamics(block, -1, mass=5.0) # كتلة ثقيلة
        
        if is_fluid and len(blocks) > 0:
            # سر آينكس: مفاصل مرنة (Spherical Joints) تمتص الصدمات
            p.createConstraint(blocks[-1], -1, block, -1, p.JOINT_POINT2POINT, 
                               [0,0,0], [0,0,0.5], [0,0,-0.5])
        
        blocks.append(block)
    return blocks

# بناء النموذجين
ainex_blocks = build_tower(-2, memory["ainex_lvl"], is_fluid=True)
legacy_blocks = build_tower(2, memory["legacy_lvl"], is_fluid=False)

# === إعداد الفيديو ===
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(VIDEO_FILENAME, fourcc, 20.0, (WIDTH, HEIGHT))

print(f">>> SIMULATION STARTED. CYCLE: {memory['total_cycles']}")

# === حلقة المحاكاة ===
for i in range(CYCLES_PER_RUN):
    # 1. تطبيق الكوارث (كل 100 فريم)
    if i % 100 == 0:
        # رياح عاتية
        wind_force = random.uniform(-20, 20)
        for b in ainex_blocks + legacy_blocks:
            p.applyExternalForce(b, -1, [wind_force, 0, 0], [0,0,0], p.WORLD_FRAME)
            
    # زلزال كل 300 فريم
    if i % 300 == 0:
        richter = random.uniform(200, 800) # قوة هائلة
        print(f"!!! EARTHQUAKE MAGNITUDE: {richter} !!!")
        for b in ainex_blocks + legacy_blocks:
            # ضربة من الأسفل للأعلى
            p.applyExternalForce(b, -1, [0, 0, richter], [0,0,0], p.WORLD_FRAME)

    # 2. خطوة فيزيائية
    p.stepSimulation()

    # 3. الرندر (التصوير)
    # الكاميرا تنظر للبرجين
    viewMatrix = p.computeViewMatrix(
        cameraEyePosition=[0, -8, 5],
        cameraTargetPosition=[0, 0, 2],
        cameraUpVector=[0, 0, 1])
    
    projectionMatrix = p.computeProjectionMatrixFOV(
        fov=60.0, aspect=float(WIDTH)/HEIGHT, nearVal=0.1, farVal=100.0)

    # التقاط الصورة (TinyRenderer - CPU based)
    width, height, rgbImg, depthImg, segImg = p.getCameraImage(
        WIDTH, HEIGHT, viewMatrix, projectionMatrix, shadow=1, renderer=p.ER_TINY_RENDERER)
    
    # تحويل الصورة لنسق يفهمه OpenCV
    img = np.reshape(rgbImg, (height, width, 4))[:, :, :3] # إزالة قناة الشفافية
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # إضافة نصوص HUD
    cv2.putText(img, f"AINEX (FLUID): LVL {memory['ainex_lvl']}", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    cv2.putText(img, f"LEGACY (SOLID): LVL {memory['legacy_lvl']}", (400, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    out.write(img)

# === الحفظ والنهاية ===
out.release()
p.disconnect()

# تحديث الذاكرة
memory["total_cycles"] += CYCLES_PER_RUN
memory["disasters_survived"] += 1
# آينكس ينمو دائماً
memory["ainex_lvl"] += 1
# القديم ينمو ببطء
if random.random() > 0.5: memory["legacy_lvl"] += 1

with open(MEMORY_FILE, 'w') as f:
    json.dump(memory, f)

print(">>> EVIDENCE GENERATED & MEMORY UPDATED.")
